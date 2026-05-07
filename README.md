# Tech Wiki

技術資料を Markdown で蓄積・タグ付け・ツリー表示・レンダリングするナレッジベースシステム。

現在の構成はローカル運用前提です。Docker、MySQL、Nginx は外し、Django + SQLite + Vite の直起動に寄せています。

## アーキテクチャ

```
Browser → Vite (:5173)
           └─ /api/* → Django + DRF (:8000) → SQLite (data/db.sqlite3)
```

| レイヤー | 技術 |
|----------|------|
| Frontend | React 19 + Vite 6 (MPA 2画面) |
| Backend | Django 5 + Django REST Framework + django-mptt |
| Database | SQLite 3 |
| 図表 | react-markdown + remark-gfm + mermaid.js |
| コードハイライト | highlight.js |
| Run | run.sh / ローカル直起動 |

## 画面構成 (MPA)

| ページ | パス | 機能 |
|--------|------|------|
| ホーム | `/` | タグツリー + 検索 + ノート一覧 |
| ノート閲覧 | `/note/{slug}` | Markdownレンダリング (mermaid対応) |
| ノート編集 | `/note/{slug}/edit` | HackMD風 split editor + preview |
| 新規ノート | `/note/new/edit` | 新規作成 |

## 起動手順

```bash
# 1. ローカル起動
bash run.sh

# 2. ブラウザでアクセス
open http://127.0.0.1:5173
```

backend だけ起動したい場合:

```bash
cd backend
source .venv/bin/activate
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8000
```

frontend だけ起動したい場合:

```bash
cd frontend
npm install
npm run dev
```

## REST API

| Method | Endpoint | 説明 |
|--------|----------|------|
| GET | `/api/v1/categories/` | カテゴリツリー（再帰） |
| GET | `/api/v1/notes/` | ノート一覧 (`?category__slug=`, `?tag=`, `?search=`) |
| POST | `/api/v1/notes/` | ノート作成 |
| GET | `/api/v1/notes/{slug}/` | ノート詳細 |
| PATCH | `/api/v1/notes/{slug}/` | ノート更新 |
| DELETE | `/api/v1/notes/{slug}/` | ノート削除 |
| POST | `/api/v1/notes/{slug}/toggle_bookmark/` | ブックマーク切替 |
| GET | `/api/v1/tags/` | 動的タグ一覧 |
| GET | `/api/v1/health/` | ヘルスチェック |

## ディレクトリ構造

```
tech-wiki/
├── .gitignore
├── run.sh
├── backend/
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── wiki/
│       ├── models.py          # Category(MPTT), Note
│       ├── serializers.py     # DRF Serializers
│       ├── views.py           # ViewSets
│       ├── urls.py            # Router
│       ├── admin.py
│       └── management/commands/
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── note.html
│   └── src/
│       ├── main.jsx           # Home entry
│       ├── note.jsx           # Note viewer/editor entry
│       ├── App.jsx            # Home page component
│       ├── NotePage.jsx       # Note detail component
│       ├── NoteEditorPage.jsx # HackMD風 editor
│       ├── api/               # API client layer
│       │   ├── client.js
│       │   ├── categories.js
│       │   └── notes.js
│       └── components/
│           ├── TagTree.jsx/.css
│           ├── NoteList.jsx/.css
│           ├── SearchBar.jsx/.css
│           ├── MermaidBlock.jsx
│           └── MarkdownRenderer.jsx/.css
└── docs/plans/
    ├── 2026-05-06-tech-wiki-design.md
    └── 2026-05-06-tech-wiki-plan.md
```

## メモ

- 認証は未導入です。ローカル環境での利用を前提にしています。
- タグは content 内の frontmatter または HackMD 形式の `###### tags:` から自動抽出します。
