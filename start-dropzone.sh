#!/bin/bash
# Tech-Wiki Dropzone Watcher
# MD ファイルを dropzone/ に置くと自動で Note として登録される
# 使い方: ./start-dropzone.sh [監視ディレクトリ]
#
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/backend"

echo "🚀 Tech-Wiki Dropzone 起動中..."
exec .venv/bin/python manage.py dropzone ${1:+--dir "$1"}
