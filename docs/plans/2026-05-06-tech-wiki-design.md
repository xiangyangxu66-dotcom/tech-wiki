# Tech-Wiki システム設計書

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 技術資料をMarkdownで蓄積・タグ付け・ツリー表示・レンダリングするナレッジベースシステム

**Architecture:** Nginx → (React Vite MPA + Django REST API) + MySQL。Nginx の単一オリジンでCORS回避。フロントはMPA（複数HTMLエントリポイント）方式。

**Tech Stack:** React 19 + Vite 6, Django 5 + DRF, MySQL 8, Nginx, Docker Compose, react-markdown + mermaid

---

## システムアーキテクチャ

```
Browser
  │
  ▼
Nginx (:80)
  ├── /api/v1/*  ──► Django + DRF (:8000) ──► MySQL (:3306)
  │                   └── /data/markdown/ (MDファイル実体)
  └── /*         ──► Vite Dev Server (:5173) or Static Build
```

**MPA エントリポイント:**
| ページ | HTML | JS Entry | 機能 |
|--------|------|----------|------|
| ホーム | `index.html` | `src/main.jsx` | カテゴリツリー + 記事一覧 + 検索 |
| 記事詳細 | `article.html` | `src/article.jsx` | Markdownレンダリング + 図表 |

---

## データモデル (Django)

```
Category (django-mptt)
├── id, name, slug, parent(FK→self), lft, rght, tree_id, level
└── 再帰的なツリー構造

Article
├── id, title, slug, file_path(相対パス→MD実体), category(FK)
├── file_size, file_hash(SHA256), content_preview(先頭200文字)
├── created_at, updated_at
└── tags (M2M → Tag)

> **設計原則:** DBにはMDファイルのパスとメタデータのみを格納。MD実体は `md_root_path` 以下の
> ファイルシステムに保存する。API経由で読み書きする際にファイルIOを行う。
> これにより DB 負荷低減・Git 管理・バックアップの分離を実現する。

Tag
├── id, name, slug
└── articles (M2M ← Article)
```

---

## REST API エンドポイント (v1)

> **API バージョニング:** `/api/v1/` で固定。将来の破壊的変更は `/api/v2/` に分離する。

### コアAPI

| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/api/v1/categories/` | カテゴリツリー全取得 |
| GET/POST | `/api/v1/categories/` | 一覧/作成 |
| GET/PUT/DELETE | `/api/v1/categories/{id}/` | 詳細/更新/削除 |
| GET | `/api/v1/articles/` | 記事一覧 (?category=, ?tag=, ?search=) |
| POST | `/api/v1/articles/` | 記事作成（file_path 指定） |
| GET/PUT/DELETE | `/api/v1/articles/{slug}/` | 記事詳細/更新/削除 |
| GET | `/api/v1/tags/` | タグ一覧 |

### ファイル入力API

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/api/v1/articles/upload/` | MDファイルアップロード（multipart/form-data） | 認証必須 |
| POST | `/api/v1/articles/paste/` | MDテキスト貼り付け（JSON body → ファイル保存 → Article作成） | 認証必須 |

### 全文検索API

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/search/?q=キーワード` | 記事全文検索（MySQL FULLTEXT + ngram） | 不要 |
| GET | `/api/v1/search/suggest/?q=キ` | サジェスト（先頭一致、最大10件） | 不要 |


## 全文検索

### 技術選定: MySQL FULLTEXT INDEX + ngram parser

MySQL 8.0 組み込みの全文検索を使用。外部サービス不要、Docker 環境で追加依存ゼロ。

| 項目 | 設定 |
|------|------|
| パーサー | `ngram`（N=2） |
| 最小/最大トークンサイズ | `innodb_ft_min_token_size=2, innodb_ft_max_token_size=84` |
| 検索モード | `NATURAL LANGUAGE MODE`（通常検索）+ `BOOLEAN MODE`（高度検索） |

### インデックス

```sql
ALTER TABLE wiki_article ADD FULLTEXT INDEX ft_article_search (title, content_preview) WITH PARSER ngram;
```

> `content_preview`（先頭200文字）をインデックス対象とする。
> ファイル実体全文のリアルタイム検索はファイルIOが重いため、
> 記事登録時に `content_preview` を更新し、それを検索対象にする。
> 深い全文検索が必要になったら Tier 2（SudachiPy）にアップグレード。

### Django ORM での検索

```python
from django.db.models import Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector  # Postgres only - not used

# MySQL FULLTEXT は Django の SearchQuery 非対応のため raw SQL または extra() を使用
class ArticleSearchBackend:
    def search(self, query: str):
        return Article.objects.raw(
            'SELECT *, MATCH(title, content_preview) AGAINST (%s IN NATURAL LANGUAGE MODE) AS relevance '
            'FROM wiki_article '
            'WHERE MATCH(title, content_preview) AGAINST (%s IN NATURAL LANGUAGE MODE) '
            'ORDER BY relevance DESC',
            [query, query]
        )
```

### Tier 2 移行条件（将来）

以下のいずれかに達したら SudachiPy + 形態素解析に移行:
- 記事数 > 5,000 件
- ngram の「誤ヒット」（「東京」で「京都」がヒットする等）への不満が顕在化
- 検索品質の定量的改善が必要になった

### サジェスト機能

`GET /api/v1/search/suggest/?q=キ` → タイトルの先頭一致で最大10件返却。
全文検索とは別に、`title` カラムに `INDEX idx_title (title)` で対応。

```python
articles = Article.objects.filter(title__istartswith=query).values('title', 'slug')[:10]
```


## ファイル入力

### 2つの入力インターフェース

```
┌─────────────────────────────┐  ┌─────────────────────────────┐
│  ① 貼り付け (Paste)         │  │  ② ファイルアップロード       │
│                             │  │                             │
│  ┌───────────────────────┐  │  │  [ファイルを選択]  button    │
│  │ # タイトル             │  │  │  📄 django-guide.md         │
│  │                       │  │  │                             │
│  │ 本文...               │  │  │  カテゴリ: [Django ▼]       │
│  │                       │  │  │  タグ:     [入門] [中級]     │
│  └───────────────────────┘  │  │                             │
│  カテゴリ: [Python ▼]      │  │  [アップロード]              │
│  タグ:     [入門] [中級]    │  └─────────────────────────────┘
│  [保存]                     │
└─────────────────────────────┘
```

### ① 貼り付け (Paste) API

```http
POST /api/v1/articles/paste/
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Djangoモデル設計メモ",
  "markdown": "# Djangoモデル設計\n\n## 概要\n...",
  "category_id": 3,
  "tag_ids": [1, 2]
}

Response 201:
{
  "id": 42,
  "title": "Djangoモデル設計メモ",
  "slug": "django-model-design-memo",
  "file_path": "programming/python/django-model-design-memo.md",
  "file_size": 2048,
  "file_hash": "a1b2c3d4...",
  ...
}
```

**バックエンド処理フロー:**
1. タイトルから slug + ファイル名を生成
2. `md_root_path/{category_path}/{filename}.md` にファイル書き込み
3. SHA256 ハッシュ計算
4. 先頭200文字を `content_preview` に抽出
5. Article レコード作成（`file_path` に相対パスを保存）

### ② ファイルアップロード API

```http
POST /api/v1/articles/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: (binary, .mdファイル)
title: "Djangoモデル設計メモ"    ← 省略時はファイル名から生成
category_id: 3
tag_ids: [1, 2]

Response 201: (同上)
```

### ファイル命名ルール

```
md_root_path/                          ← SystemConfig で設定。例: /data/markdown
└── {カテゴリのslugパス}/
    └── {article.slug}.md
```

例: カテゴリ `プログラミング > Python > Django` の記事 `django-model-design` は
`/data/markdown/programming/python/django/django-model-design.md` に保存。

カテゴリ未設定の場合は `md_root_path/uncategorized/{slug}.md`。

### 競合時の挙動

| ケース | 挙動 |
|--------|------|
| 同名ファイル既存 | `file_hash` を比較。同一ならスキップ（重複登録しない）。異なるなら `{slug}-2.md` に退避 |
| slug 重複 | paste の場合は `{slug}-{timestamp}.md`、upload の場合は `{original_name}-{timestamp}.md` |


## 認証 (JWT)

### 技術選定

- **パッケージ:** `djangorestframework-simplejwt` — DRF 標準の JWT 認証ライブラリ
- **User モデル:** Django 標準 `auth.User`（カスタマイズ不要）
- **トークン方式:** Access Token（短期） + Refresh Token（長期）。Access が切れたら Refresh で再発行

### トークン設計

| 項目 | 値 | 理由 |
|------|-----|------|
| Access Token 有効期限 | 30分 | セキュリティと利便性のバランス |
| Refresh Token 有効期限 | 7日 | 頻繁なログインを避ける |
| トークン形式 | Bearer (Authorization ヘッダー) | 標準的 |
| identity | `str(user.id)` | simplejwt のデフォルト |

### 認証 API エンドポイント

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| POST | `/api/v1/auth/register/` | ユーザー登録 | 不要 |
| POST | `/api/v1/auth/login/` | ログイン → access + refresh 返却 | 不要 |
| POST | `/api/v1/auth/refresh/` | Refresh トークンで Access Token 再発行 | Refresh Token |
| GET | `/api/v1/auth/me/` | 現在のユーザー情報取得 | Access Token |
| POST | `/api/v1/auth/logout/` | ログアウト（Refresh Token 無効化） | Access Token |

### 保護ポリシー（ViewSet 別）

| エンドポイント | GET (参照) | POST (作成) | PUT/PATCH (更新) | DELETE (削除) |
|---------------|-----------|-------------|-----------------|---------------|
| `/api/v1/articles/` | 認証不要 | 認証必須 | — | — |
| `/api/v1/articles/{slug}/` | 認証不要 | — | 認証必須 | 認証必須 |
| `/api/v1/articles/upload/` | — | 認証必須 | — | — |
| `/api/v1/articles/paste/` | — | 認証必須 | — | — |
| `/api/v1/categories/` | 認証不要 | Admin のみ | Admin のみ | Admin のみ |
| `/api/v1/tags/` | 認証不要 | 認証必須 | 認証必須 | Admin のみ |
| `/api/v1/search/` | 認証不要 | — | — | — |
| `/api/v1/config/` | 認証不要 | — | Admin のみ | — |
| `/api/v1/logs/` | Admin のみ | — | — | — |

### AuditLog との連携

```python
# ViewSet の perform_create/update/destroy で request.user を AuditLog に記録
class ArticleViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        article = serializer.save()
        AuditLog.objects.create(
            action='CREATE', model_name='Article',
            object_id=article.id, object_repr=str(article),
            user=self.request.user if self.request.user.is_authenticated else None,
        )
```

### フロントエンドの認証フロー

```
1. ユーザーがログインフォームに username + password を入力
2. POST /api/v1/auth/login/ → access_token + refresh_token を localStorage に保存
3. 以降の API リクエストに Authorization: Bearer <access_token> を付与
4. 401 が返ったら refresh_token で POST /api/v1/auth/refresh/ を試行
5. refresh も失敗したらログイン画面にリダイレクト
6. ログアウト時は localStorage を消去 + POST /api/v1/auth/logout/ でサーバー側も無効化
```

### MPA での認証状態管理

SPA と違いページ遷移で再初期化されるため、`localStorage` のトークンを各ページのエントリポイントで読み込み、ユーザー情報を毎回 `/api/v1/auth/me/` で取得する。

### 画面追加

| ページ | HTML | JS Entry | 機能 |
|--------|------|----------|------|
| ログイン | `login.html` | `src/login.jsx` | ログインフォーム + 新規登録リンク |
| ユーザー登録 | `register.html` | `src/register.jsx` | 登録フォーム |

### 有効期限の環境変数管理

```python
# settings.py
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('JWT_ACCESS_MINUTES', 30))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,   # リフレッシュ時に新しい Refresh Token も発行
    'BLACKLIST_AFTER_ROTATION': True, # 古い Refresh Token を無効化
}
```


## ヘルスチェック

### エンドポイント

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/health/` | 簡易ヘルスチェック（DB接続確認のみ） | 不要 |
| GET | `/api/v1/health/detailed/` | 詳細ヘルス（DB, ディスク, メモリ） | Admin のみ |

### レスポンス形式

```json
// GET /api/v1/health/
{
  "status": "healthy",
  "timestamp": "2026-05-06T15:30:00+09:00",
  "checks": {
    "database": "ok",
    "uptime_seconds": 12345
  }
}

// GET /api/v1/health/detailed/ （Admin only）
{
  "status": "healthy",
  "timestamp": "2026-05-06T15:30:00+09:00",
  "checks": {
    "database": "ok",
    "disk_usage_percent": 45.2,
    "memory_usage_percent": 62.1,
    "uptime_seconds": 12345
  },
  "version": "1.0.0"
}
```

### Docker 連携

```yaml
# docker-compose.yml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/"]
    interval: 30s
    timeout: 5s
    retries: 3
```

### フロントエンド表示

- 全ページ共通のフッターに **システムステータスインジケーター**（🟢/🔴 ドット）を配置
- クリックすると詳細モーダルを展開（DB状態、稼働時間を表示）
- 30秒ごとに `/api/v1/health/` をポーリングして状態を更新
- `/api/v1/health/` が 3 回連続失敗したら異常と判断し 🔴 表示


## 例外設計


例外は `backend/exceptions/` に集約し、システム例外と業務例外に大別する。
例外設計の詳細は `docs/specs/exception-design.md`、エラーコード定義は `docs/specs/error-codes.md` にてそれぞれ一元管理する。

> **2つのドキュメントの役割:**
> - **exception-design.md** → 開発者向け。例外クラス階層・ハンドラ・送出ルール・テスト方針
> - **error-codes.md** → エンドユーザー（+フロントエンド）向け。エラーコード一覧・メッセージ・画面挙動。変更時はフロントエンド担当者との合意が必要

```
backend/exceptions/
├── __init__.py          # 全例外のエクスポート
├── base.py              # 基底例外クラス
├── system.py            # システム例外 (500系)
└── business.py          # 業務例外 (400系 / 404系)
```

### 例外階層

```
AppError (基底)
├── SystemError (システム例外)
│   ├── DatabaseError        # DB接続・クエリ失敗
│   ├── FileSystemError      # MarkdownファイルIO失敗
│   ├── ConfigError          # 設定不正
│   └── ExternalServiceError # 外部サービス障害
│
└── BusinessError (業務例外)
    ├── NotFoundError         # リソース不在 (→ 404)
    ├── ValidationError       # バリデーション失敗 (→ 400)
    ├── DuplicateError        # 重複 (→ 409)
    └── ForbiddenError        # 権限不足 (→ 403)
```

### DRF 例外ハンドラ

`config/error_handler.py` で DRF の `EXCEPTION_HANDLER` をカスタムし、
全例外を以下の統一形式で返す:

```json
{
  "error": {
    "code": "E04001",
    "message": "タイトルは必須です",
    "detail": "Article.title が空です",
    "timestamp": "2026-05-06T15:30:00+09:00"
  }
}
```

### エラーコード体系

| プレフィックス | 分類 | HTTP Status |
|---------------|------|-------------|
| `E01xxx` | システム例外 | 500 |
| `E02xxx` | システム例外（DB） | 500 |
| `E03xxx` | システム例外（ファイルIO） | 500 |
| `E04xxx` | 業務例外（バリデーション） | 400 |
| `E05xxx` | 業務例外（認証・認可） | 401/403 |
| `E06xxx` | 業務例外（リソース不在） | 404 |
| `E07xxx` | 業務例外（重複・競合） | 409 |

詳細は `docs/specs/error-codes.md` 参照。

---

## Config 機能

### .env 管理（インフラ層・変更時再起動が必要）

```bash
# docker-compose.yml が参照
NGINX_PORT=80
BACKEND_PORT=8000
FRONTEND_PORT=5173
MYSQL_PORT=3306
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=techwiki
MYSQL_USER=wiki
MYSQL_PASSWORD=wikipass

# Django settings.py が参照
DJANGO_SECRET_KEY=xxx
DEBUG=1
LOG_LEVEL=INFO
```

### SystemConfig モデル（DB管理・管理画面から動的変更可能）

```python
class SystemConfig(models.Model):
    key         = models.CharField(max_length=100, unique=True)
    value       = models.TextField()
    description = models.CharField(max_length=255, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    # 想定キー:
    # site_name              → "Tech-Wiki"
    # site_description       → "技術資料ナレッジベース"
    # articles_per_page      → "20"
    # md_root_path           → "/data/markdown"
    # enable_mermaid         → "true"
    # enable_syntax_highlight → "true"
```

### Config API

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/config/` | 全件 or ?key=xxx で1件取得 | 認証不要 |
| PUT | `/api/v1/config/{id}/` | 値更新 | Admin only |

---

## Log 機能 (AuditLog)

### モデル

```python
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', '作成'),
        ('UPDATE', '更新'),
        ('DELETE', '削除'),
        ('VIEW',   '閲覧'),
    ]
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=100)
    object_id   = models.PositiveIntegerField(null=True)
    object_repr = models.CharField(max_length=500)
    changes     = models.JSONField(null=True, blank=True)
    user        = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL)
    ip_address  = models.GenericIPAddressField(null=True)
    user_agent  = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)
```

### ログ採取タイミング

| トリガー | action | 方法 |
|---------|--------|------|
| 記事/カテゴリ/タグ 作成 | CREATE | ViewSet.perform_create() |
| 記事/カテゴリ/タグ 更新 | UPDATE | ViewSet.perform_update() |
| 記事/カテゴリ/タグ 削除 | DELETE | ViewSet.perform_destroy() |
| 記事詳細表示 | VIEW | ViewSet.retrieve() （負荷次第でON/OFF）|

### Log API

| Method | Endpoint | 説明 | 認証 |
|--------|----------|------|------|
| GET | `/api/v1/logs/` | ログ一覧（action/model_name フィルタ可） | Admin only |
| GET | `/api/v1/logs/stats/` | 集計（日別PV、記事別アクセス数） | Admin only |

### Django アプリケーションログ（settings.py LOGGING）

```python
LOGGING = {
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'when': 'midnight',
            'backupCount': 30,
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django':      {'handlers': ['file', 'console'], 'level': 'WARNING'},
        'wiki':        {'handlers': ['file', 'console'], 'level': 'INFO'},
        'audit':       {'handlers': ['file'], 'level': 'INFO'},
    },
}
```

---

## フロントエンド コンポーネント構成

```
Home Page (main.jsx)
├── Sidebar
│   ├── CategoryTree         ← 再帰ツリーコンポーネント
│   └── SearchBar
├── ArticleList              ← 記事カード一覧
└── TagCloud                 ← タグクラウド

Article Page (article.jsx)
├── ArticleHeader            ← タイトル/タグ/日付
├── MarkdownRenderer         ← react-markdown + mermaid
│   ├── CodeBlock (mermaid)  ← mermaid図の動的レンダリング
│   └── Custom components    ← テーブル/画像/コードハイライト
└── ArticleNav               ← 前後記事ナビゲーション
```
