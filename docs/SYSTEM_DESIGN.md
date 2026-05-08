# Tech-Wiki システム設計書

> **Version**: 2026年5月版（Beta）
> **プロジェクト種別**: 個人ナレッジベース
> **生成対象**: NotebookLM 投げ込み用

---

## 1. プロジェクトの目的と背景

### 1.1 なぜ技術ノートを集約するのか

エンジニアとして日々蓄積される技術調査の成果物——特定ライブラリの検証コード、アーキテクチャ検討のメモ、トラブルシュートの記録——は、通常ディレクトリやブックマークに散在し、半年後には「あれどこだっけ」になる。

Tech-Wiki はこれらを **Markdown ファイルという可搬性の高い形式で一箇所に集約し、全文検索とタグ分類で即座に引き出せる** 個人ナレッジベースである。

### 1.2 設計思想

| 原則 | 意味 |
|------|------|
| **ファイル優先** | データは Markdown ファイルが正。DB は検索インデックスに過ぎない |
| **ドロップゾーン** | ディレクトリにファイルを置くだけでインポート。運用コストゼロ |
| **検索第一** | タグより全文検索。探す手間を最小化 |
| **シンプルスタック** | SQLite + Django REST + React。個人運用で過剰な依存は持たない |

---

## 2. システムアーキテクチャ概要

### 2.1 6層スタック

```
┌─────────────────────────────────────────┐
│ 6. Presentation    React 19 + Vite      │  UI、MPAルーティング
├─────────────────────────────────────────┤
│ 5. Edge             Vite dev proxy      │  CORS解決、API転送
├─────────────────────────────────────────┤
│ 4. API              Django REST         │  JSON API、認証（将来）
├─────────────────────────────────────────┤
│ 3. Logic            Service/Repository  │  ビジネスロジック分離
├─────────────────────────────────────────┤
│ 2. Search           SQLite FTS5         │  全文検索エンジン
├─────────────────────────────────────────┤
│ 1. Data             SQLite              │  永続化
└─────────────────────────────────────────┘
```

### 2.2 技術選定の理由

| 技術 | 選定理由 | 捨てた選択肢 |
|------|---------|-------------|
| **Django 5** | REST Framework の完成度、管理コマンド機構、テスト充実 | Flask（認証・ORM を自前で積むコスト高） |
| **SQLite** | 個人用で十分な性能。FTS5 全文検索が標準装備。バックアップは `cp` 一発 | MySQL/PostgreSQL（個人用に別プロセス運用は過剰） |
| **React 19 + Vite** | MPA 構成でもコンポーネント再利用可能。Vite の HMR が高速 | Next.js（SSR 不要な個人ツールに重量級） |
| **MPA（Multi Page App）** | 編集ページは独立した HTML エントリポイント。URL 直リンク可能 | SPA（CSR だと `/note/xxx/edit` の直リンクが面倒） |
| **FTS5** | `MATCH` 構文 + `REGEXP` の二段構えで柔軟な全文検索 | Elasticsearch（運用コストに見合わない） |
| **Markdown** | 可搬性・可読性・Git 管理との相性 | リッチテキスト（DB ロックイン、検索困難） |

### 2.3 MPA 構成の意図

```
/index.html          → ノート一覧 + 全文検索（メイン画面）
/note/{slug}/edit    → 単一ノート編集（独立HTMLエントリポイント）
```

編集画面を独立させた理由：
- `/note/react-hooks/edit` をブックマーク可能
- 一覧画面の状態（検索クエリ・スクロール位置）を破壊しない
- 将来の認証追加時にページ単位でガード可能

---

## 3. コアデータモデル

### 3.1 Note エンティティ

```python
class Note(models.Model):
    slug = models.SlugField(unique=True, max_length=255)
    title = models.CharField(max_length=500)
    content = models.TextField()
    content_hash = models.CharField(max_length=64)  # SHA256 for change detection
    note_tags = models.JSONField(default=list)       # ["Python", "Django", "FTS5"]
    category_name = models.CharField(max_length=200, blank=True)
    category_slug = models.SlugField(max_length=200, blank=True)
    bookmark = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='published')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source_file = models.CharField(max_length=500, blank=True)  # 元MDファイルパス
```

### 3.2 Tag の設計判断：なぜ ManyToMany ではなく JSON Array か

**結論**: `JSONField(default=list)` を採用。`ManyToManyField` は採用しない。

| 観点 | JSON Array | ManyToMany |
|------|-----------|------------|
| タグ追加の手間 | ファイルの frontmatter に `tags: [X]` と書くだけ | Tag モデル行の事前INSERTが必要 |
| 重複排除 | アプリ側で `list(set(tags))` | DB の UNIQUE 制約 |
| ファイル→DB 同期 | そのまま上書き | 中間テーブルの差分更新が必要 |
| クエリ | `note_tags` カラムの JSON クエリ | JOIN で取得 |
| 整合性 | ゆるい（タイポがそのまま入る） | 固い（FK制約） |

テックノートのタグは「そのファイルを書いた人の主観ラベル」であり、統制語彙（controlled vocabulary）にする必要性が低い。むしろ柔軟に付与できることを優先した。

### 3.3 FTS5 全文検索インデックス

```sql
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title,
    content,
    note_tags,
    content=notes,
    content_rowid=id
);

-- INSERT/UPDATE/DELETE の自動同期
CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, content, note_tags)
    VALUES (new.id, new.title, new.content, new.note_tags);
END;
```

トリガーでメインテーブルと FTS 仮想テーブルを自動同期。アプリ側は `Note.save()` を呼ぶだけで検索インデックスが最新になる。

---

## 4. 全文検索の仕組み

### 4.1 FTS5 + REGEXP の二段構え

```
ユーザー入力 "Python async"
        │
        ▼
┌─ FTS5 MATCH ──────────────────────┐
│ SELECT * FROM notes_fts            │
│ WHERE notes_fts MATCH 'Python async'│  ← トークン化・前方一致
│ ORDER BY rank                       │
└──────────────┬─────────────────────┘
               │ 結果が 0 件 or 「すべて表示」要求時
               ▼
┌─ REGEXP フォールバック ────────────┐
│ SELECT * FROM notes                │
│ WHERE title REGEXP '(?i)Python'     │  ← 部分一致・正規表現
│    OR content REGEXP '(?i)Python'   │
│    OR note_tags REGEXP '(?i)Python' │
│ ORDER BY updated_at DESC            │
└────────────────────────────────────┘
```

**なぜ FTS5 だけでは不十分か**：
- FTS5 のデフォルト tokenizer は CJK（日中韓）文字を適切にトークン化できない
- 2文字以下の検索語（`Go`、`C`、`R`）が MATCH でヒットしない
- 技術用語の略語（`K8s`、`gRPC`）がトークン化で壊れる

**解決策**: FTS5 を第一パス（高速・高精度）に使い、フォールバックで REGEXP（遅いが網羅的）に切り替える。日本語技術文書の検索では REGEXP 側に倒れるケースが多いが、32 notes 程度のデータ量なら全件スキャンでも実用上の遅延はない（~5ms）。

### 4.2 Content Snippet 抽出

FTS5 の `snippet()` 関数は CJK 非対応のため、自前で実装：

```python
def _regexp_snippet(content, search_terms, context_chars=120):
    """REGEXP でヒット箇所を見つけ、前後 context_chars を切り出す"""
```

検索語の出現位置から前後120文字を抽出し、`<mark>` タグでハイライト。複数ヒットがある場合は最大2スニペットまで返す。

### 4.3 言語混在対応

日本語・中国語・英語が混在するノートに対し：
- FTS5 は `unicode61` tokenizer（デフォルト）を使用。英語のステミングは無効化して完全一致寄りに
- REGEXP は Unicode フラグ `(?i)` で大文字小文字を無視
- タグ列（JSON Array）も検索対象に含めることで、「タグ名でフィルタ」と「キーワードで全文検索」を単一クエリで実現

---

## 5. ドロップゾーン（ファイル取込）

### 5.1 アーキテクチャ

```
┌──────────────────────────────────────────────────┐
│ dropzone/incoming/                                │
│ ├── Vue使用指南.md         ← ユーザーが置く        │
│ └── Dockerメモ.md                                  │
└──────────┬───────────────────────────────────────┘
           │ watchdog (PollingObserver)
           ▼
┌──────────────────┐     ┌──────────────────┐
│  ファイル読込    │────▶│  frontmatter抽出  │
│  (MDパース)      │     │  title, tags, …   │
└──────────────────┘     └────────┬─────────┘
                                  ▼
                        ┌──────────────────┐
                        │  content_hash    │
                        │  による重複判定   │──▶ 変更なし → skip
                        └────────┬─────────┘
                                 │ 変更あり or 新規
                                 ▼
                        ┌──────────────────┐
                        │  Note.save()     │
                        │  ├─ slug生成      │
                        │  ├─ FTS5同期      │
                        │  └─ processed/ 移動│
                        └──────────────────┘
```

### 5.2 設計判断

**なぜ watchdog + ディレクトリ監視か**：
- 「ファイルを置く」という行為はエンジニアにとって最も自然なインポート操作
- Web UI でのアップロードより、Finder → ディレクトリへのドラッグ＆ドロップが早い
- 監視方式により、HackMD で書いたノートをエクスポートして置くだけで自動反映

**なぜ `content_hash` で重複判定か**：
- タイムスタンプ比較は信頼性が低い（git clone で全ファイル更新される等）
- SHA256 ハッシュで「内容が変わったか」を正確に判定
- 変更がないファイルは DB 更新をスキップ → 同じファイルを何度置いても無駄な I/O なし

### 5.3 HackMD エクスポート対応

HackMD からエクスポートした Markdown には行番号接頭辞が付与される：

```
   399|###### tags: `chatbot`
```

これに対応するため、タグ抽出の正規表現は行番号接頭辞をスキップする：

```python
HACKMD_TAGS_RE = r'^\s*(?:\d+\|\s*)*#{1,6}\s*tags:\s*(`.+?`[\s,]*)+$'
```

### 5.4 パフォーマンス実測値

| 処理 | 時間 |
|------|------|
| 1ファイル（Django起動含む） | 0.38s |
| 5新規ファイル INSERT（FTS 込み） | 0.40s |
| 23ファイル一括インポート | 2秒以内 |

ボトルネックは Django 起動時のアプリロード（~0.2s）。ファイル処理自体は 1件あたり ~10ms。

**「遅い」と誤認された原因**：Django の `OutputWrapper` が非TTY出力を完全バッファリング。`--once` モード（一括処理後即終了）を追加して解決。

---

## 6. API 設計

### 6.1 リソース設計

```
GET    /api/v1/notes/          一覧（?q= &tag= &page= &page_size= &sort=）
GET    /api/v1/notes/{slug}/   単一ノート
POST   /api/v1/notes/          新規作成
PATCH  /api/v1/notes/{slug}/   部分更新
DELETE /api/v1/notes/{slug}/   削除
POST   /api/v1/notes/{slug}/toggle_bookmark/  ブックマーク切替

GET    /api/v1/tags/           タグ一覧（使用頻度順）
GET    /api/v1/health/         ヘルスチェック
```

### 6.2 統一エラー形式

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "ノートが見つかりません: xxx"
  }
}
```

- `code` は機械可読（フロントエンドのエラーハンドリング分岐に使う）
- `message` は人間可読（UI 表示用）
- バリデーションエラーはフィールド名を key にした詳細マップで返す

### 6.3 ページネーション・検索・ソート

- `page` / `page_size` でオフセットベースのページング
- `q` パラメータで全文検索（FTS5 → REGEXP フォールバック）
- `tag` パラメータでタグフィルタリング
- `sort` パラメータで `updated` / `created` / `title` ソート
- レスポンスに `total` / `page` / `page_size` / `total_pages` を含む

---

## 7. フロントエンド設計

### 7.1 コンポーネントツリー

```
App.jsx
├── HealthIndicator           ← API死活表示（右上）
├── SearchBar                 ← 全文検索入力（IME対応）
├── TagTree                   ← タグ一覧（サイドバー）
└── NoteList                  ← ノート一覧
    ├── ブックマークセクション
    │   └── NoteCard (mode=list|icon)
    └── タググループセクション
        ├── セクションディバイダー
        ├── NoteCard × N
        └── ページネーション（タグ単位・10件/頁）

NoteEditorPage.jsx            ← 独立MPAページ
├── タイトル入力
├── MarkdownRenderer（プレビュー）
└── 保存/キャンセル

MarkdownRenderer.jsx
├── ReactMarkdown + remark-gfm
├── highlight.js（コードハイライト）
└── MermaidBlock（図表レンダリング、lazy load）
```

### 7.2 状態管理

- **グローバル状態なし**。Redux/MobX 不使用
- データフェッチは各ページコンポーネントの `useEffect` 内で `api.*()` を直接呼ぶ
- ブックマーク切替は楽観的更新（UI 即時反映 → API 失敗時にロールバック）
- 検索状態は `SearchBar` が `window.location.search` と同期（URL 共有可能）

### 7.3 検索UI

- **IME 対応**: `composingRef` で IME 変換中の Enter による誤送信を防止
- **複合検索**: タイトル検索 + コンテンツ検索の2入力。両方指定時は OR 結合
- **検索トリガー**: ボタンクリック or Enter キー
- **結果表示**: `<mark>` タグでヒット語をハイライト

---

## 8. テスト戦略とカバレッジ

### 8.1 テスト構成

| 層 | フレームワーク | テスト数 | カバレッジ（Statements） |
|----|--------------|---------|--------------------------|
| バックエンド | pytest + pytest-django | 223 | 78% |
| フロントエンド | vitest + Testing Library | 111 | **94.2%** |

### 8.2 バックエンドテスト戦略

- **モデルテスト**: `Note.save()` の slug 自動生成、FTS5 同期、タグ重複排除
- **API テスト**: `APIClient` を使った統合テスト。認証なし（現状）
- **検索テスト**: FTS5 MATCH、REGEXP フォールバック、CJK、複合検索
- **コマンドテスト**: `call_command('dropzone', '--once')` の一括インポート

### 8.3 フロントエンドテスト戦略

- **API レイヤー**: `vi.fn()` で `fetch` をモック。HTTP ステータス分岐、エラーパース、204 No Content、カスタムヘッダーをカバー
- **コンポーネント**: Testing Library でユーザー操作をシミュレート。`fireEvent` + `userEvent` 併用
- **非同期**: `waitFor` で Suspense / lazy load の解決を待つ
- **カバレッジターゲット**: 新規コードは 90% 以上を維持

### 8.4 カバレッジレポート

HTML レポートは `docs/coverage/` に永続化し、Git 管理下に置く（`.gitignore` しない）。`scripts/coverage.sh` で後端・前端両方のレポートを一括再生成可能。

---

## 9. 開発インフラ

### 9.1 プロジェクト構造

```
tech-wiki/
├── backend/                  # Django 5 + DRF
│   ├── config/               # settings.py, urls.py, wsgi.py
│   ├── wiki/                 # メインアプリ
│   │   ├── models.py         # Note モデル + FTS5 トリガー
│   │   ├── views.py          # APIView + 検索ロジック
│   │   ├── serializers.py    # DRF Serializer
│   │   ├── urls.py           # ルーティング
│   │   └── management/commands/dropzone.py  # ファイル取込
│   └── tests/                # pytest テスト
├── frontend/                 # React 19 + Vite
│   ├── src/
│   │   ├── api/              # client.js, notes.js
│   │   ├── components/       # NoteCard, NoteList, SearchBar, …
│   │   └── NoteEditorPage.jsx
│   ├── tests/                # vitest テスト
│   └── vite.config.js        # MPA 設定
├── docs/
│   ├── coverage/             # カバレッジレポート（Git管理）
│   └── SYSTEM_DESIGN.md      # 本ドキュメント
├── scripts/
│   └── coverage.sh           # カバレッジ一括再生成
├── dropzone/
│   ├── incoming/             # 監視ディレクトリ
│   └── processed/            # 処理済ファイル
└── .gitignore
```

### 9.2 環境管理

- `backend/.env` に `SECRET_KEY`、`DEBUG` 等を格納（.gitignore 対象）
- テンプレートとして `backend/.env.example` をリポジトリに含める
- `pip` の依存関係は `backend/requirements.txt`（本番用）と `backend/requirements-dev.txt`（開発用）に分割

### 9.3 Git 運用

- **ブランチ戦略**: `main` 一本。個人プロジェクトのため feature ブランチは必要な時のみ
- **コミットメッセージ**: Conventional Commits（`feat:`, `fix:`, `test:`, `docs:`, `chore:`）
- **リモート**: Gitee（中国国内のアクセス速度を考慮）
- **プッシュ前チェック**: テスト全件パス + カバレッジレポート更新 を手動実行

### 9.4 現在のステータス（2026年5月）

| 項目 | 状態 |
|------|------|
| バックエンド API | ✅ 全CRUD + 検索 + ドロップゾーン |
| フロントエンド UI | ✅ 一覧・検索・編集・ブックマーク |
| 全文検索 | ✅ FTS5 + REGEXP 二段構え |
| ファイル取込 | ✅ watchdog + content_hash 重複判定 |
| テスト | ✅ Backend 223 / Frontend 111 |
| カバレッジ | ✅ Frontend 94.2% / Backend 78% |
| 認証 | 🔲 未実装（個人用のため後回し） |
| バックアップ | 🔲 未実装（SQLite なので `cp` で代用可能） |
| RBAC | 🔲 未実装（個人用のため不要） |
