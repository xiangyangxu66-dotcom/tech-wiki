# 全文検索 設計書

## 概要

既存の DRF SearchFilter（`LIKE '%kw%'`）を SQLite FTS5 + カラム別重み + 日本語 trigram 分割に置き換える。UI も一行二入力に改修。

## 1. 検索アーキテクチャ

```
ユーザー入力
  ├─ タイトル検索: FTS5 MATCH (title カラム, 重み 10)
  ├─ 内容検索: FTS5 MATCH (content カラム, 重み 1) / REGEXP 切替可能
  └─ 両方指定時: INTERSECT (AND 条件)
```

### 1.1 FTS5 仮想テーブル

```sql
CREATE VIRTUAL TABLE wiki_note_fts USING fts5(
    title,
    content,
    tokenize='trigram'  -- 3文字スライド窓で日本語部分一致を実現
);
```

- `trigram`: 「全文検索」→ `全文検` `文検索` → 「検索」で部分一致ヒット
- 英数字は通常通りトークナイズされる

### 1.2 検索パラメータ

| パラメータ | 型 | 説明 |
|---|---|---|
| `search_title` | string | タイトル FTS5 検索 |
| `search_content` | string | 内容 FTS5 検索 |
| `search_content_pattern` | string | 内容 正規表現検索（指定時は FTS5 を迂回） |
| `search` | string | 後方互換: 従来の `?search=` も残す（title+content 統合 FTS5） |

### 1.3 bm25 重み付け

```
bm25(wiki_note_fts, 10.0, 1.0)
```

| カラム | 重み | 理由 |
|---|---|---|
| title | 10.0 | タイトル一致は強いシグナル |
| content | 1.0 | 本文一致は補助的 |

## 2. UI

### 2.1 レイアウト

```
┌─ 検索 ───────────────────────────────────────────┐
│  T  [  タイトルを検索...  ]   C  [  内容を検索...  ]  .* │
└───────────────────────────────────────────────────┘
```

- `T` / `C`: ミニラベル（title / content）
- `.*`: regexp モード切替ボタン。押下で内容入力が「RegExp 検索」に切り替わる。没押时は FTS5
- フォーカス時全体に薄枠強調
- Escape で全クリア

### 2.2 状態遷移

| 操作 | 結果 |
|---|---|
| タイトル入力 + Enter | タイトル FTS5 検索 |
| 内容入力 + Enter | 内容 FTS5 検索 |
| `.*` ON + 内容入力 | 内容正規表現検索（WHERE content REGEXP '…'） |
| 両方入力 | AND 条件（INTERSECT） |
| Escape | 全クリア → 全件表示に戻す |
| クリアボタン | 当該フィールドのみクリア |

### 2.3 パラメータマッピング

```js
// SearchBar → App
onSearch({ title, content, useRegexp })
```

App 側で `useNotes` に渡し、API 呼び出し時に以下パラメータを付与:

```js
const params = {};
if (title) params.search_title = title;
if (content && !useRegexp) params.search_content = content;
if (content && useRegexp) params.search_content_pattern = content;
```

## 3. API レスポンス（snippet 付き）

### 3.1 既存

```json
{
  "count": 29,
  "results": [
    {
      "id": 1,
      "slug": "terraform",
      "title": "terraform基本",
      "note_tags": ["terraform", "aws"],
      "updated_at": "2026-05-07T10:00:00Z"
    }
  ]
}
```

### 3.2 検索時追加

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "slug": "terraform",
      "title": "terraform基本",
      "note_tags": ["terraform", "aws"],
      "updated_at": "2026-05-07T10:00:00Z",
      "_snippet": "...terraform は HashiCorp が開発..."
    }
  ]
}
```

- `_snippet`: 内部用フィールド。シリアライザには含めず、view で注入
- FTS5 非使用時（全件表示 / タグフィルター）は付与しない

## 4. 実装ステップ

| # | 内容 | ファイル |
|---|---|---|
| 1 | FTS5 migration を trigram に変更 | `wiki/migrations/0004_note_fts5.py` |
| 2 | FTS5SearchFilter: title/content 分離 + regexp 分岐 | `wiki/fts_search.py` |
| 3 | NoteListSerializer に snippet 追加 | `wiki/serializers.py` |
| 4 | NoteViewSet: snippet 注入ロジック | `wiki/views.py` |
| 5 | UI: SearchBar 一行二入力 + regexp 切替 | `SearchBar.jsx` / `.css` |
| 6 | App.jsx: onSearch → searchParams 受渡変更 | `App.jsx` |
| 7 | notes.js: fetchNotes パラメータ追加 | `api/notes.js` |
| 8 | NoteList: snippet 表示 | `NoteList.jsx` / `.css` |
| 9 | テスト（migration + API + UI） | |

## 5. 後方互換

- 既存タグ: `?tag=aws` は全件 FTS5 × タグフィルタ
- 既存 `?search=` は title+content 統合 FTS5 として残す
- 新パラメータ `search_title` / `search_content` は既存 `search` と共存（どちらか一方のみ有効とし、新パラメータ優先）
