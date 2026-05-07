-- ============================================================================
-- Tech-Wiki シードデータ (Pure SQL DML)
-- MySQL コンテナ初回起動時に /docker-entrypoint-initdb.d/ から自動実行。
-- 本シードは Django models.py の構造に同期しています。
-- ============================================================================
SET NAMES utf8mb4;

-- ======================================
-- CATEGORIES (MPTT — lft/rght/tree_id/level)
-- ======================================
INSERT INTO wiki_category (id, name, slug, parent_id, lft, rght, tree_id, level, description, created_at) VALUES
-- ROOT ノード群 (tree_id=1,2,3,4)
(1,  'プログラミング', 'puroguramingu', NULL, 1, 10, 1, 0, 'プログラミング言語・フレームワーク', '2026-04-01 00:00:00'),
(2,  'Python',         'python',         1,    2, 7,  1, 1, 'Pythonエコシステム',              '2026-04-01 00:00:00'),
(3,  'Django',         'django',         2,    3, 4,  1, 2, 'Djangoフルスタックフレームワーク', '2026-04-01 00:00:00'),
(4,  'FastAPI',        'fastapi',        2,    5, 6,  1, 2, '高速APIフレームワーク',           '2026-04-01 00:00:00'),
(5,  'JavaScript',     'javascript',     1,    8, 9,  1, 1, 'JavaScriptフロントエンド',        '2026-04-01 00:00:00'),

(6,  'インフラ',       'infura',         NULL, 1, 6,  2, 0, 'インフラ・DevOps',               '2026-04-01 00:00:00'),
(7,  'Docker',         'docker',          6,   2, 3,  2, 1, 'コンテナ仮想化',                  '2026-04-01 00:00:00'),
(8,  'Kubernetes',     'kubernetes',      6,   4, 5,  2, 1, 'コンテナオーケストレーション',    '2026-04-01 00:00:00'),

(9,  'データベース',   'detabesu',        NULL, 1, 6,  3, 0, 'DBMS全般',                       '2026-04-01 00:00:00'),
(10, 'MySQL',          'mysql',           9,   2, 3,  3, 1, 'MySQL 8.0+',                     '2026-04-01 00:00:00'),
(11, 'PostgreSQL',     'postgresql',      9,   4, 5,  3, 1, 'PostgreSQL',                     '2026-04-01 00:00:00')
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- ======================================
-- NOTES（技術ノート）— note_tags は JSON 配列
-- ======================================
INSERT INTO wiki_note (id, title, slug, content, note_tags, category_id, bookmark, status, created_at, updated_at) VALUES
(1,
 'Django REST Framework 入門',
 'django-rest-framework-rumen',
 '# Django REST Framework 入門\n\n## 概要\n\nDjango REST Framework（DRF）は Django で RESTful API を構築するための強力なツールキット。\n\n## 主要機能\n\n### Serializer\n\n```python\nfrom rest_framework import serializers\nfrom .models import Note\n\nclass NoteSerializer(serializers.ModelSerializer):\n    class Meta:\n        model = Note\n        fields = [''id'', ''title'', ''slug'', ''content'', ''status'']\n```\n\n### ViewSet\n\n```python\nfrom rest_framework import viewsets\n\nclass NoteViewSet(viewsets.ModelViewSet):\n    queryset = Note.objects.all()\n    serializer_class = NoteSerializer\n```\n\n### Router\n\n```python\nfrom rest_framework.routers import DefaultRouter\n\nrouter = DefaultRouter()\nrouter.register(r''notes'', NoteViewSet)\n```\n\n## アーキテクチャ\n\n```mermaid\ngraph TD\n    A[Client] --> B[ViewSet]\n    B --> C[Serializer]\n    C --> D[Model]\n    D --> E[(MySQL)]\n```\n\n## 参考\n\n- [DRF公式ドキュメント](https://www.django-rest-framework.org/)\n- [Classy DRF](https://www.cdrf.co/)',
 '["入門", "チートシート"]',
 3, 1, 'published', '2026-04-01 09:00:00', '2026-05-01 12:00:00'),

(2,
 'React 19 + Vite プロジェクト構成',
 'react-19-vite-project-setup',
 '# React 19 + Vite プロジェクト構成\n\n## 環境構築\n\n```bash\nnpm create vite@latest frontend -- --template react\ncd frontend\nnpm install\n```\n\n## MPA ルーティング戦略\n\nVite で MPA（Multi Page Application）を構築する場合、`rollupOptions.input` で複数エントリポイントを指定する。\n\n```javascript\n// vite.config.js\nexport default defineConfig({\n  build: {\n    rollupOptions: {\n      input: {\n        main: resolve(__dirname, ''src/main.jsx''),\n        login: resolve(__dirname, ''src/pages/login.jsx''),\n        dashboard: resolve(__dirname, ''src/pages/dashboard.jsx''),\n      }\n    }\n  }\n})\n```\n\n## パフォーマンス最適化\n\n### コード分割\n\n```javascript\nconst NoteDetail = lazy(() => import(''./pages/NoteDetail''));\n```\n\n### Bundle Analyzer\n\n```bash\nnpm install --save-dev rollup-plugin-visualizer\n```\n\n## 参考\n\n- [Vite公式ガイド](https://vitejs.dev/)\n- [React 19 新機能](https://react.dev/blog/2024/12/05/react-19)',
 '["中級", "アーキテクチャ"]',
 5, 1, 'published', '2026-04-15 14:00:00', '2026-05-03 10:00:00'),

(3,
 'Docker Compose 開発環境構築',
 'docker-compose-dev-setup',
 '# Docker Compose 開発環境構築\n\n## 構成\n\n```\nproject/\n├── docker-compose.yml\n├── backend/\n│   └── Dockerfile\n├── frontend/\n│   └── Dockerfile\n└── nginx/\n    └── nginx.conf\n```\n\n## docker-compose.yml\n\n```yaml\nversion: ''3.9''\nservices:\n  db:\n    image: mysql:8.0\n    environment:\n      MYSQL_ROOT_PASSWORD: rootpass\n      MYSQL_DATABASE: techwiki\n    volumes:\n      - mysql_data:/var/lib/mysql\n    ports:\n      - ''3306:3306''\n\n  backend:\n    build: ./backend\n    depends_on:\n      - db\n    environment:\n      DB_HOST: db\n\n  frontend:\n    build: ./frontend\n    ports:\n      - ''5173:5173''\n\n  nginx:\n    image: nginx:alpine\n    ports:\n      - ''80:80''\n    volumes:\n      - ./nginx/nginx.conf:/etc/nginx/nginx.conf\n    depends_on:\n      - backend\n      - frontend\n\nvolumes:\n  mysql_data:\n```\n\n## よくあるトラブル\n\n### MySQL起動待ち問題\n\n`depends_on` だけでは不十分。`wait-for-it.sh` または `healthcheck` を併用する。\n\n```yaml\nhealthcheck:\n  test: [\"CMD\", \"mysqladmin\", \"ping\", \"-h\", \"localhost\"]\n  timeout: 20s\n  retries: 10\n```\n\n## 参考\n\n- [Docker Compose 公式](https://docs.docker.com/compose/)',
 '["入門", "チュートリアル"]',
 7, 1, 'published', '2026-04-20 11:00:00', '2026-05-02 08:00:00'),

(4,
 'MySQL FULLTEXT INDEX 日本語全文検索',
 'mysql-fulltext-ngram',
 '# MySQL FULLTEXT INDEX 日本語全文検索\n\n## N-gram パーサーの概要\n\nMySQL 8.0 の `ngram` パーサーは、日本語などのスペース区切りがない言語の全文検索に有効。\n\n```sql\nALTER TABLE wiki_note\n  ADD FULLTEXT INDEX ft_note_search (title, content) WITH PARSER ngram;\n```\n\n## 検索クエリ\n\n```sql\n-- 自然言語検索\nSELECT * FROM wiki_note\nWHERE MATCH(title, content) AGAINST(''Django ORM'' IN NATURAL LANGUAGE MODE);\n\n-- ブーリアンモード\nSELECT * FROM wiki_note\nWHERE MATCH(title, content) AGAINST(''+Django -SQL'' IN BOOLEAN MODE);\n```\n\n## N-gram の N 値\n\n```sql\n-- デフォルト ngram_token_size=2（バイグラム）\nSET GLOBAL ngram_token_size = 2;\n```\n\nバイグラムは「東京」→「東京」でヒット。ユニグラム(N=1)では「京」→「東京」「京都」と過剰ヒット。\n\n## 制約\n\n- 最小検索語長: `innodb_ft_min_token_size`\n- ストップワード: デフォルトリストに注意\n\n## 参考\n\n- [MySQL 8.0 FULLTEXT リファレンス](https://dev.mysql.com/doc/refman/8.0/en/fulltext-search.html)',
 '["上級", "チートシート"]',
 10, 1, 'published', '2026-04-25 16:00:00', '2026-05-05 09:00:00'),

(5,
 'Nginx リバースプロキシ設定テンプレート',
 'nginx-reverse-proxy-template',
 '# Nginx リバースプロキシ設定テンプレート\n\n## 単一オリジン構成（CORS不要）\n\n```nginx\nupstream backend {\n    server backend:8000;\n}\n\nupstream frontend_dev {\n    server frontend:5173;\n}\n\nserver {\n    listen 80;\n    server_name localhost;\n\n    # API → Django\n    location /api/ {\n        proxy_pass http://backend;\n        proxy_set_header Host $host;\n        proxy_set_header X-Real-IP $remote_addr;\n    }\n\n    # Admin\n    location /admin/ {\n        proxy_pass http://backend;\n    }\n\n    # 静的ファイル（本番）\n    location / {\n        root /usr/share/nginx/html;\n        try_files $uri /index.html;\n    }\n}\n```\n\n## 開発モード（Vite HMR対応）\n\n```nginx\nlocation / {\n    proxy_pass http://frontend_dev;\n    proxy_http_version 1.1;\n    proxy_set_header Upgrade $http_upgrade;\n    proxy_set_header Connection \"upgrade\";\n}\n```\n\n## セキュリティヘッダ\n\n```nginx\nadd_header X-Content-Type-Options nosniff;\nadd_header X-Frame-Options DENY;\nadd_header X-XSS-Protection \"1; mode=block\";\n```\n\n## 参考\n\n- [nginx公式ドキュメント](https://nginx.org/en/docs/)',
 '["中級", "チートシート"]',
 7, 0, 'published', '2026-04-28 10:00:00', '2026-05-04 15:00:00'),

(6,
 'FastAPI 非同期ハンドリングパターン',
 'fastapi-async-patterns',
 '# FastAPI 非同期ハンドリングパターン\n\n## 同期 vs 非同期\n\n```python\nfrom fastapi import FastAPI\nimport asyncio\nimport time\n\napp = FastAPI()\n\n# 同期エンドポイント — スレッドプールで実行\n@app.get(\"/sync\")\ndef sync_endpoint():\n    time.sleep(1)          # スレッドをブロック\n    return {\"status\": \"ok\"}\n\n# 非同期エンドポイント — イベントループで実行\n@app.get(\"/async\")\nasync def async_endpoint():\n    await asyncio.sleep(1)  # イベントループをブロックしない\n    return {\"status\": \"ok\"}\n```\n\n## DB クエリの注意点\n\nSQLAlchemy の同期的な操作はスレッドプールで実行する必要がある。\n\n```python\nfrom sqlalchemy.ext.asyncio import create_async_engine, AsyncSession\n\nengine = create_async_engine(\"mysql+aiomysql://user:pass@db/techwiki\")\n\n@app.get(\"/notes\")\nasync def list_notes():\n    async with AsyncSession(engine) as session:\n        result = await session.execute(select(Note))\n        return result.scalars().all()\n```\n\n## アーキテクチャ\n\n```mermaid\nsequenceDiagram\n    participant Client\n    participant FastAPI\n    participant DB\n    Client->>FastAPI: GET /notes\n    FastAPI->>DB: await session.execute()\n    DB-->>FastAPI: rows\n    FastAPI-->>Client: JSON\n```\n\n## 参考\n\n- [FastAPI 並行性](https://fastapi.tiangolo.com/async/)',
 '["中級"]',
 4, 0, 'published', '2026-05-01 08:00:00', '2026-05-02 14:00:00'),

(7,
 'Kubernetes Pod トラブルシュート集',
 'kubernetes-pod-troubleshoot',
 '# Kubernetes Pod トラブルシュート集\n\n## CrashLoopBackOff\n\n### 症状\n\n```bash\nkubectl get pods\n# NAME       READY   STATUS             RESTARTS   AGE\n# myapp-pod  0/1     CrashLoopBackOff   12         30m\n```\n\n### 調査コマンド\n\n```bash\n# ログ確認\nkubectl logs myapp-pod --previous\n\n# イベント確認\nkubectl describe pod myapp-pod\n\n# コンテナ内コマンド実行（起動中のみ）\nkubectl exec -it myapp-pod -- /bin/sh\n```\n\n### 原因別対処\n\n| 原因 | 対処 |\n|------|------|\n| OOMKilled | resources.limits.memory 増加 |\n| ImagePullBackOff | imagePullSecrets 確認 / レジストリアクセス権限 |\n| 起動スクリプトエラー | command/args 確認 |\n| Readiness Probe 失敗 | initialDelaySeconds 延長 |\n\n## Pending（スケジュール不可）\n\n```bash\nkubectl describe pod myapp-pod | grep -A5 Events\n# 0/3 nodes are available: 3 Insufficient cpu.\n```\n\n→ リソースリクエスト削減 または ノード追加\n\n## 参考\n\n- [kubectl チートシート](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)\n- [Pod Lifecycle](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)',
 '["トラブルシュート", "上級"]',
 8, 0, 'draft', '2026-05-03 13:00:00', '2026-05-05 13:00:00'),

(8,
 'PostgreSQL パフォーマンスチューニング',
 'postgresql-performance-tuning',
 '# PostgreSQL パフォーマンスチューニング\n\n## 基本パラメータ\n\n```ini\n# postgresql.conf\n\n# メモリ\nshared_buffers = 4GB              # RAM の 25%\neffective_cache_size = 12GB       # RAM の 75%\nwork_mem = 64MB                   # ソート/ハッシュ用\nmaintenance_work_mem = 1GB        # VACUUM/CREATE INDEX 用\n\n# プランナー\nrandom_page_cost = 1.1            # SSD の場合\nseq_page_cost = 1.0\neffective_io_concurrency = 200    # SSD の場合\n\n# WAL\nwal_buffers = 64MB\nmax_wal_size = 4GB\ncheckpoint_timeout = 15min\n```\n\n## スロークエリ調査\n\n```sql\n-- スロークエリログ有効化\nALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1秒以上\nSELECT pg_reload_conf();\n\n-- pg_stat_statements で集計\nCREATE EXTENSION pg_stat_statements;\n\nSELECT query, calls, mean_exec_time, total_exec_time\nFROM pg_stat_statements\nORDER BY total_exec_time DESC\nLIMIT 10;\n```\n\n## インデックス戦略\n\n```sql\n-- 複合インデックス\nCREATE INDEX idx_note_category_status ON wiki_note(category_id, status);\n\n-- 部分インデックス\nCREATE INDEX idx_bookmarked ON wiki_note(updated_at) WHERE bookmark = true;\n\n-- BRIN インデックス（大規模テーブル）\nCREATE INDEX idx_note_created_brin ON wiki_note USING BRIN(created_at);\n```\n\n## 参考\n\n- [PostgreSQL Wiki - Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)\n- [pg_stat_statements](https://www.postgresql.org/docs/current/pgstatstatements.html)',
 '["上級"]',
 11, 0, 'draft', '2026-05-04 10:00:00', '2026-05-05 16:00:00'),

(9,
 'Git コミットメッセージ規約',
 'git-commit-convention',
 '# Git コミットメッセージ規約\n\n## Conventional Commits\n\n```\n<type>(<scope>): <subject>\n\n<body>\n\n<footer>\n```\n\n### Type 一覧\n\n| Type     | 用途                   |\n|----------|------------------------|\n| feat     | 新機能                 |\n| fix      | バグ修正               |\n| docs     | ドキュメント変更       |\n| style    | フォーマット（空白等） |\n| refactor | リファクタリング       |\n| perf     | パフォーマンス改善     |\n| test     | テスト追加・修正       |\n| chore    | ビルド・CI 等          |\n\n### 例\n\n```\nfeat(note): add bookmark field for priority display\n\nブックマークされたノートをリスト先頭に表示するため、\nNote モデルに bookmark boolean フィールドを追加。\n\nCloses #42\n```\n\n### 破壊的変更\n\n```\nfeat(api)!: rename Article to Note\n\nBREAKING CHANGE: /api/v1/articles/ → /api/v1/notes/\n```\n\n## Git フックで強制\n\n```bash\n# commit-msg フック\n#!/bin/sh\ncommit_regex=''^(feat|fix|docs|style|refactor|perf|test|chore)(\\(.+\\))?: .{1,50}''\nif ! grep -qE \"$commit_regex\" \"$1\"; then\n    echo \"コミットメッセージが Conventional Commits 形式に従っていません\"\n    exit 1\nfi\n```\n\n## 参考\n\n- [Conventional Commits](https://www.conventionalcommits.org/)',
 '["入門"]',
 NULL, 0, 'published', '2026-04-10 09:00:00', '2026-05-03 11:00:00'),

(10,
 'Python デコレータ完全理解',
 'python-decorator-deep-dive',
 '# Python デコレータ完全理解\n\n## 基本形\n\n```python\nimport functools\n\ndef log_call(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        print(f\"Calling {func.__name__}\")\n        result = func(*args, **kwargs)\n        print(f\"{func.__name__} returned {result}\")\n        return result\n    return wrapper\n\n@log_call\ndef add(a, b):\n    return a + b\n\nadd(3, 5)\n# Calling add\n# add returned 8\n# 8\n```\n\n## 引数付きデコレータ\n\n```python\ndef retry(max_attempts=3, delay=1):\n    def decorator(func):\n        @functools.wraps(func)\n        def wrapper(*args, **kwargs):\n            for attempt in range(max_attempts):\n                try:\n                    return func(*args, **kwargs)\n                except Exception as e:\n                    if attempt == max_attempts - 1:\n                        raise\n                    time.sleep(delay * (2 ** attempt))\n        return wrapper\n    return decorator\n\n@retry(max_attempts=5, delay=2)\ndef unstable_network_call():\n    ...\n```\n\n## クラスベースデコレータ\n\n```python\nclass CountCalls:\n    def __init__(self, func):\n        functools.update_wrapper(self, func)\n        self.func = func\n        self.count = 0\n\n    def __call__(self, *args, **kwargs):\n        self.count += 1\n        print(f\"{self.func.__name__} called {self.count} times\")\n        return self.func(*args, **kwargs)\n```\n\n## スタッキング\n\n```python\n@log_call\n@retry(max_attempts=3)\n@measure_time\ndef process_data():\n    ...\n# 実行順: measure_time → retry → log_call → process_data\n```\n\n## 実践パターン: Django ビューデコレータ\n\n```python\nfrom functools import wraps\nfrom django.http import JsonResponse\n\ndef require_auth(view_func):\n    @wraps(view_func)\n    def wrapper(request, *args, **kwargs):\n        if not request.user.is_authenticated:\n            return JsonResponse({\"error\": \"Unauthorized\"}, status=401)\n        return view_func(request, *args, **kwargs)\n    return wrapper\n```\n\n## 参考\n\n- [PEP 318 – Decorators](https://peps.python.org/pep-0318/)\n- [Real Python – Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)',
 '["中級", "チートシート"]',
 2, 0, 'published', '2026-03-15 10:00:00', '2026-04-20 16:00:00')
ON DUPLICATE KEY UPDATE title=VALUES(title);

-- ======================================
-- SystemConfig 初期値
-- ======================================
INSERT INTO wiki_systemconfig (`key`, value, description) VALUES
('site.title',       'Tech-Wiki',         'サイトタイトル'),
('site.description', '技術資料ナレッジベース', 'サイト説明'),
('pagination.size',  '20',                'ノート一覧の1ページあたりの表示件数')
ON DUPLICATE KEY UPDATE value=VALUES(value);
