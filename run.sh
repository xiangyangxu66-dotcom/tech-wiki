#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "============================================"
echo "  Tech-Wiki — ローカル開発起動"
echo "============================================"

# オプション: --dropzone でファイル監視も同時起動
WITH_DROPZONE=0
if [[ "$1" == "--dropzone" ]]; then
    WITH_DROPZONE=1
    shift
fi

# ── Backend (Django) ──────────────────────
echo ""
echo "[1/3] Django マイグレーション + シード投入..."
cd "$ROOT/backend"
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

python manage.py migrate --run-syncdb

echo "[2/3] Django 起動 (port 8000)..."
python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# ── Dropzone watcher (optional) ──────────
DROPZONE_PID=""
if [[ $WITH_DROPZONE -eq 1 ]]; then
    echo "[dropzone] ファイル監視開始 → dropzone/"
    python -u manage.py dropzone > /tmp/tech-wiki-dropzone.log 2>&1 &
    DROPZONE_PID=$!
    echo "  dropzone (PID=$DROPZONE_PID)"
fi

# ── Frontend (Vite) ──────────────────────
echo "[3/3] Vite 起動 (port 5173)..."
cd "$ROOT/frontend"
npm install --silent 2>/dev/null || true
npm run dev &
VITE_PID=$!

# ── Cleanup ──────────────────────────────
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $DJANGO_PID 2>/dev/null || true
    kill $VITE_PID 2>/dev/null || true
    [[ -n "$DROPZONE_PID" ]] && kill $DROPZONE_PID 2>/dev/null || true
    wait
    echo "Done."
}
trap cleanup INT TERM

echo ""
echo "============================================"
echo "  Ready!"
echo "  フロントエンド → http://localhost:5173"
echo "  API (direct)   → http://localhost:8000/api/v1/"
if [[ $WITH_DROPZONE -eq 1 ]]; then
    echo "  dropzone       → dropzone/ (MD投げ込みで自動登録)"
    echo "  dropzone log   → tail -f /tmp/tech-wiki-dropzone.log"
fi
echo "============================================"

wait
