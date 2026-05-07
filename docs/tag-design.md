# タグ機能 設計仕様書 v2

**Status: CONFIRMED — Option B (Tag テーブル + M2M)** | 2026-05-08

---

## 0. 判断

**Option B で確定。** 理由はユーザーの指摘の通り：

> カテゴリはこのwikiに足りたてる概念の一つで、もう一つは全文検索です。
> この二つがなかったら、ただ単にファイルの山です。

タグもまた Wiki を「ファイルの山」から「構造化知識ベース」に昇華させる柱の一つ。
Category（MPTT ツリー）と全文検索（FTS5）に並ぶ第三の軸として、Tag を独立テーブルで正規化する。

---

## 1. DB 設計

### 1.1 Tag テーブル（新設）

```python
class Tag(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    slug       = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
```

**あえてシンプルに。** description/color 等のメタデータは YAGNI。Tag テーブルの役割は (a) 存在の正規化 (b) SQL による効率的集計・絞り込み (c) 参照カウントによる自動クリーンアップ。この3つに絞る。

### 1.2 Note.tags M2M（既存 note_tags を置換）

```python
class Note(models.Model):
    ...
    tags = models.ManyToManyField(Tag, related_name='notes', blank=True)
    # note_tags = JSONField(...)  ← ★ 削除
```

### 1.3 移行戦略

`0001_initial.py` はまだ本番データがないので、**0001 を直接修正して初期化し直す。** 本番運用開始前のため、migration の積み重ねは不要。

```sql
-- 実質的な操作
ALTER TABLE wiki_note DROP COLUMN note_tags;
CREATE TABLE wiki_tag (...);
CREATE TABLE wiki_note_tags (...);  -- Django auto M2M intermediate
```

### 1.4 ER 図

```
┌──────────────┐       ┌──────────────────┐       ┌──────┐
│    Note      │       │  note_tags (M2M)  │       │ Tag  │
├──────────────┤       ├──────────────────┤       ├──────┤
│ id           │──┐    │ id               │    ┌──│ id   │
│ title        │  └───→│ note_id (FK)     │    │  │ name │
│ content      │       │ tag_id (FK)      │←───┘  │ slug │
│ category_id  │       └──────────────────┘       │ ...  │
│ content_hash │                                   └──────┘
│ has_mermaid  │
│ bookmark     │       ┌──────────────┐
│ status       │       │  Category    │
│ created_at   │       ├──────────────┤
│ updated_at   │──┐    │ id           │
└──────────────┘  └───→│ name         │
                        │ slug         │
                        │ parent_id    │
                        │ lft/rght     │
                        └──────────────┘
```

---

## 2. タグライフサイクルと Source of Truth

### 2.1 真理源（Single Source of Truth）

**content の frontmatter が真理源。** これは変えない。

```
タグ生成・編集の流れ:
  1. content に tags: [Python, FastAPI]  ← 真理源
  2. Note.save() → extract_tags_from_content() → Tag.objects.get_or_create() → M2M同期
  3. DB の tags M2M は派生データ（キャッシュに近い）
```

**エディタでタグを編集した場合:**
```
  1. ユーザーが UI で tags を変更
  2. PATCH /api/v1/notes/{slug}/  →  { "tags_slugs": ["python", "fastapi"] }
  3. バックエンドで:
     a. content の frontmatter tags: 行を整形
     b. Note.save() → 自動で M2M 同期
```

### 2.2 0参照タグのクリーンアップ

```python
# Note.save() の最後、またはシグナルで
Tag.objects.annotate(note_count=Count('notes')).filter(note_count=0).delete()
```

**すべての Note から参照が消えたタグは自動削除。** 明示的な DELETE API は不要。

### 2.3 タグ編集の制約

- タグ名のリネーム → 不可（Tag.name は immutable）
- タグの削除 → 参照が0になれば自動（手動削除API不要）
- タグの新規作成 → Note.content frontmatter 経由で自動

---

## 3. API 設計

### 3.1 Note API（変更あり）

**`GET /api/v1/notes/`** — リスト

```json
{
  "results": [
    {
      "id": 1,
      "title": "Python 入門",
      "slug": "python-intro",
      "tags": [
        {"name": "Python", "slug": "python"},
        {"name": "入門", "slug": "ru-men"}
      ],
      "category": {...},
      "bookmark": false,
      "status": "published",
      ...
    }
  ]
}
```

**変更点**: `note_tags: ["Python"]` → `tags: [{"name": "Python", "slug": "python"}]`

**`POST/PUT/PATCH /api/v1/notes/{slug}/`** — 作成・更新

```json
// Request (PATCH で tags だけ更新)
{
  "tags": ["python", "fastapi"]   // slug の配列
}
// または
{
  "tag_slugs": ["python", "fastapi"]
}
```

**変更点**: `note_tags` read_only → `tag_slugs` writable。save() で content frontmatter 同期 + M2M 同期。

### 3.2 タグ集計 API（実装変更）

**`GET /api/v1/tags/`**

```json
[
  {"name": "Python", "slug": "python", "count": 5},
  {"name": "Docker", "slug": "docker", "count": 3},
  {"name": "無所属", "count": 2}
]
```

**実装変更**: Python 全件ループ → SQL `Tag.objects.annotate(note_count=Count('notes'))`

### 3.3 タグ絞り込み（実装変更）

**`GET /api/v1/notes/?tag=python`**

**実装変更**: Python `values_list` ループ → SQL `Note.objects.filter(tags__slug='python')`

### 3.4 タグ一覧 API（新規）

**`GET /api/v1/tags/list/`** — 全タグ一覧（集計なし、エディタの補完用）

```json
[
  {"name": "Python", "slug": "python"},
  {"name": "Docker", "slug": "docker"}
]
```

---

## 4. 画面設計

### 4.1 TagTree（サイドバー）— 変更なし

```
┌─ Sidebar ──────────────────────────┐
│ 🔍 検索ボックス                     │
│ ┌─ TagTree ──────────────────────┐ │
│ │ 📌 ブックマーク (2)             │ │
│ │ 🏷️ タグ                        │ │
│ │   Python (5)                   │ │
│ │   Docker (3)                   │ │
│ │   Flask (2)                    │ │
│ │   無所属 (2)                    │ │
│ └────────────────────────────────┘ │
└────────────────────────────────────┘
```

データ構造が `{name, count}` → `{name, slug, count}` に変わるだけ。UI は変わらない。
クリックで `?tag=python`（slug）で絞り込み。

### 4.2 NotePage（詳細）— タグ表示追加

```
┌─ NotePage ─────────────────────────┐
│ タイトル: Python 入門               │
│ カテゴリ: infra/python              │
│ タグ: [Python] [入門] [FastAPI]    │  ← ★ 追加
│ 更新日: 2026-05-08                  │
│ ────────────────────────────────── │
│ (本文 Markdown レンダリング)         │
└────────────────────────────────────┘
```

タグクリック → `?tag=python` で絞り込み表示に遷移。

### 4.3 NoteEditorPage — タグ編集UI追加

```
┌─ NoteEditorPage ───────────────────┐
│ タイトル: [________________]       │
│ カテゴリ: [___select___]           │
│ タグ: [Python ×] [入門 ×] [+追加]  │  ← ★ 追加
│ ────────────────────────────────── │
│ (content Markdown エディタ)         │
│                                     │
│ [保存] [キャンセル]                  │
└────────────────────────────────────┘
```

**仕様:**
- 既存タグ → バッジ表示 + ×ボタンで削除
- `+追加` → ドロップダウン（既存タグ補完） + 新規入力可
- Save 時に `tags: ["python", "ru-men"]` を API 送信
- backend の save() が content frontmatter を自動同期

---

## 5. Dropzone インポート処理の変更

```python
# 現状
note = Note.objects.create(
    title=title, slug=slug, content=content,
    note_tags=tags,  # 死にコード（save() が上書き）→ 削除済み
    category=category, status=Note.Status.PUBLISHED,
)

# 変更後：save() が extract_tags_from_content() → Tag.get_or_create() → M2M.add() を自動実行
# dropzone 側のコードは変更不要（save() が全部やる）
```

---

## 6. 実装作業

### Phase 1: スキーマ変更（バックエンド）

| # | タスク | ファイル |
|---|--------|---------|
| 1 | Tag モデル追加 | `models.py` |
| 2 | Note.note_tags → tags M2M 変更 | `models.py` |
| 3 | `extract_tags_from_content()` を M2M 同期に変更 | `models.py` → `Note.save()` |
| 4 | 0参照タグ自動クリーンアップ追加 | `models.py` / signals |
| 5 | migration リセット（0001 再生成） | `migrations/` |
| 6 | シリアライザ変更（note_tags → tags） | `serializers.py` |
| 7 | ビュー変更（tag_aggregation, tag 絞り込み） | `views.py` |
| 8 | tag_slugs 書き込み対応 + frontmatter 同期 | `views.py` + `models.py` |
| 9 | タグ一覧 API 追加 | `views.py` + `urls.py` |
| 10 | FTS5 トリガー再作成（tags M2M 用） | `search.py`？ |
| 11 | admin 更新 | `admin.py` |

### Phase 2: フロントエンド

| # | タスク | ファイル |
|---|--------|---------|
| 12 | TagTree データ構造対応 | `TagTree.jsx` |
| 13 | NotePage タグ表示 | `NotePage.jsx` |
| 14 | NoteEditorPage タグ編集UI | `NoteEditorPage.jsx` |

### Phase 3: テスト

| # | タスク | ファイル |
|---|--------|---------|
| 15 | test_models.py 更新（M2M テスト） | `test_models.py` |
| 16 | test_dropzone.py 更新（M2M テスト） | `test_dropzone.py` |
| 17 | test_api.py 更新（tags API テスト） | `test_api.py` |

---

## 7. リスクと対策

| リスク | 対策 |
|--------|------|
| frontmatter と M2M の不整合 | save() が常に content → M2M の一方向同期。ユーザーが直接 M2M を操作する経路を作らない |
| 0001 migration 再生成によるDB初期化 | 開発中なので問題なし。`db.sqlite3` 削除 → `migrate` → `dropzone --once` で復元 |
| タグ slug の一意性違反（日本語タグ） | `unique_slug()` と同じフォールバックロジックを Tag.save() にも適用 |
