# テストカバレッジレポート

最終生成: 2026-05-08

## サマリ

| 対象 | テスト数 | 行カバレッジ | 分岐カバレッジ | レポート |
|------|---------|-------------|---------------|---------|
| Backend (Django) | 223 | 78% | — | [backend/index.html](backend/index.html) |
| Frontend (React) | 42 | 79.5% | 65.9% | [frontend/index.html](frontend/index.html) |

## レポート構成

```
docs/coverage/
├── README.md          ← このファイル
├── backend/           ← pytest-cov 出力 (HTML)
│   └── index.html     ← バックエンドカバレッジトップ
└── frontend/          ← Vitest coverage-v8 出力 (HTML)
    └── index.html     ← フロントエンドカバレッジトップ
```

## 再生成方法

```bash
# 両方一括
bash scripts/coverage.sh

# 個別
cd backend && .venv/bin/pytest --cov=wiki --cov-report=html:../docs/coverage/backend
cd frontend && npx vitest run --coverage --coverage.reportsDirectory=../docs/coverage/frontend
```

各レポートは静的 HTML で、ブラウザで直接開いて閲覧可能。
