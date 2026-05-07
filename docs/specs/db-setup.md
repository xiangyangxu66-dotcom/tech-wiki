# Tech-Wiki DB 構築 & シード投入 手順書

## 前提

- MySQL 8.0 以降が起動していること
- Python 3.11+ (venv 有効)
- Django プロジェクトルート: `backend/`

---

## 1. 初回セットアップ（migration + シード）

### 1-1. migration 生成と適用

```bash
# backend/ ディレクトリで実行
cd /Users/xu/work/tech-wiki/backend

# 既存の古い migration を削除（スキーマ再設計のため）
# ※ 本番では絶対にやらない。開発初期のみ。
rm -f wiki/migrations/0*.py

# 新規 migration 作成
python manage.py makemigrations wiki

# migration 適用（DB テーブル作成）
python manage.py migrate
```

### 1-2. 動作確認

```bash
# マイグレーション状態確認
python manage.py showmigrations

# Django shell でテーブル確認
python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print([t for t in tables if t.startswith('wiki_')])
# → ['wiki_auditlog', 'wiki_category', 'wiki_note', 'wiki_note_tags', 'wiki_systemconfig', 'wiki_tag']
"
```

---

## 2. シードデータ投入

### 方式 A: Django 管理コマンド（ORM 経由）

```bash
cd /Users/xu/work/tech-wiki/backend
python manage.py seed_data
```

**スクリプト**: `wiki/management/commands/seed_data.py`
- カテゴリ（ツリー構造）、タグ、ノート、ノート-タグ紐付けを作成
- `get_or_create` 利用 → 冪等（再実行しても重複しない）

### 方式 B: 純粋 SQL（ORM 非依存）

```bash
# MySQL に直接 SQL ファイルを流し込む
mysql -u root -p techwiki < /Users/xu/work/tech-wiki/docs/specs/db-seed.sql
```

**特徴**: ORM の `save()` メソッドを通さないため slug 自動生成等は行われない。
SQL ファイル側ですでに slug 値を明示指定済み。純粋にデータ投入したい場合に使う。

### 方式 C: Docker Compose 経由

```bash
cd /Users/xu/work/tech-wiki

# DB 起動
docker compose up -d db

# SQL 流し込み
docker compose exec -T db mysql -u root -prootpass techwiki < docs/specs/db-seed.sql

# または Django shell で（backend コンテナ経由）
docker compose exec backend python manage.py seed_data
```

---

## 3. 投入データ確認

```bash
# Django shell
python manage.py shell
```

```python
from wiki.models import Note, Category, Tag, NoteTag

# カテゴリ数
print(Category.objects.count())   # → 11

# ノート数
print(Note.objects.count())       # → 10

# タグ数
print(Tag.objects.count())        # → 7

# ブックマークされたノート
print(Note.objects.filter(bookmark=True).values_list('title', flat=True))
# → ['Django REST Framework 入門', 'React 19 + Vite プロジェクト構成', 'Docker Compose 開発環境構築', 'MySQL FULLTEXT INDEX 日本語全文検索']

# 公開済みノート
print(Note.objects.filter(status='published').count())  # → 8

# カテゴリツリー確認（MPTT）
from wiki.models import Category
root = Category.objects.get(name='プログラミング')
root.get_descendants(include_self=True).values('name', 'level')
```

---

## 4. リセット（全データ削除）

```bash
# Django 管理コマンド
python manage.py flush --noinput

# または SQL で TRUNCATE
mysql -u root -p techwiki -e "
  SET FOREIGN_KEY_CHECKS=0;
  TRUNCATE TABLE wiki_note_tags;
  TRUNCATE TABLE wiki_note;
  TRUNCATE TABLE wiki_category;
  TRUNCATE TABLE wiki_tag;
  TRUNCATE TABLE wiki_auditlog;
  SET FOREIGN_KEY_CHECKS=1;
"
```

---

## 5. テーブル定義の確認

```bash
# MySQL でテーブル構造を見る
mysql -u root -p techwiki -e "SHOW CREATE TABLE wiki_note\G"
mysql -u root -p techwiki -e "SHOW INDEX FROM wiki_note;"

# 全文検索インデックス確認
mysql -u root -p techwiki -e "
  SELECT * FROM information_schema.INNODB_FT_INDEX_CACHE
  WHERE table_name = 'wiki_note';
"

# ngram パーサー設定確認
mysql -u root -p techwiki -e "SHOW VARIABLES LIKE 'ngram_token_size';"
```

---

## ファイル配置

```
tech-wiki/
├── docs/specs/
│   ├── db-schema.sql     ← DDL（テーブル定義リファレンス）
│   ├── db-seed.sql       ← DML（シードデータ）
│   └── db-setup.md       ← このファイル
└── backend/
    └── wiki/
        ├── models.py     ← Django ORM モデル
        └── management/commands/
            └── seed_data.py  ← Django 管理コマンド
```
