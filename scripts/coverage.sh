#!/usr/bin/env bash
# テストカバレッジレポート一括生成
# 使用方法: bash scripts/coverage.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== Backend (Django + pytest) ==="
cd backend
.venv/bin/pytest --cov=wiki --cov-report=html:../docs/coverage/backend
# coverage.py auto-generates a .gitignore that ignores everything.
# We use docs/coverage/ as a permanent artifact, so remove it.
rm -f ../docs/coverage/backend/.gitignore
cd ..

echo ""
echo "=== Frontend (React + Vitest) ==="
cd frontend
npx vitest run --coverage --coverage.reportsDirectory=../docs/coverage/frontend
cd ..

echo ""
echo "=== レポート ==="
echo "Backend : docs/coverage/backend/index.html"
echo "Frontend: docs/coverage/frontend/index.html"
