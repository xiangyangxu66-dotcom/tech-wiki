# Tech-Wiki Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** React Vite MPA + Django REST API + MySQL + Nginx のナレッジベースシステムをゼロから構築

**Architecture:** Nginx リバースプロキシで単一オリジン化。Django REST Framework でAPI提供。React MPA (2エントリポイント) でフロント。

**Tech Stack:** Django 5, DRF, django-mptt, MySQL 8, React 19, Vite 6, react-markdown, mermaid, highlight.js, Nginx, Docker Compose

**Design Doc:** `docs/plans/2026-05-06-tech-wiki-design.md`

---

## Phase 1: プロジェクトスキャフォールドと Docker 環境

### Task 1.1: プロジェクトルート構造と Docker Compose

**Objective:** Docker Compose で Nginx + Django + MySQL + Frontend(Node) の4サービスを定義

**Files:**
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: docker-compose.yml 作成**

```yaml
version: "3.8"
services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-rootpass}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-techwiki}
      MYSQL_USER: ${MYSQL_USER:-wiki}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-wikipass}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  backend:
    build: ./backend
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql://wiki:wikipass@db:3306/techwiki
      - DEBUG=1
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - frontend
      - backend

volumes:
  mysql_data:
```

**Step 2: .env.example 作成**

```
MYSQL_ROOT_PASSWORD=rootpass
MYSQL_DATABASE=techwiki
MYSQL_USER=wiki
MYSQL_PASSWORD=wikipass
```

**Step 3: .gitignore 作成**

```
node_modules/
__pycache__/
*.pyc
.env
mysql_data/
dist/
.vite/
```

**Step 4: Commit**

```bash
git init && git add -A && git commit -m "feat: add docker-compose and project scaffold"
```

---

### Task 1.2: Django プロジェクト初期化

**Objective:** Django 5 プロジェクト作成、MySQL 接続設定、django-mptt / DRF 導入

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/requirements.txt`
- Create: `backend/manage.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/wiki/__init__.py`
- Create: `backend/wiki/apps.py`

**Step 1: backend/Dockerfile**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
```

**Step 2: backend/requirements.txt**

```
Django>=5.0,<5.1
djangorestframework>=3.15,<3.16
django-mptt>=0.14,<0.15
mysqlclient>=2.2,<2.3
django-cors-headers>=4.3,<4.4
django-filter>=24.1,<25.0
gunicorn>=22.0,<23.0
```

**Step 3: Django プロジェクト作成**

```bash
cd backend
pip install -r requirements.txt  # venv内で
django-admin startproject config .
python manage.py startapp wiki
```

**Step 4: config/settings.py 設定**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'mptt',
    'corsheaders',
    'django_filters',
    # Local
    'wiki',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE', 'techwiki'),
        'USER': os.environ.get('MYSQL_USER', 'wiki'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD', 'wikipass'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}
```

**Step 5: Commit**

```bash
git add backend/ && git commit -m "feat: scaffold Django project with DRF and mptt"
```

---

### Task 1.3: Django モデル定義

**Objective:** Category (MPTT), Article, Tag の3モデルを作成

**Files:**
- Create: `backend/wiki/models.py`
- Create: `backend/wiki/admin.py`

**Step 1: models.py**

```python
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(MPTTModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='children'
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=500, unique=True)
    content = models.TextField()  # Markdown content
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='articles'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
```

**Step 2: admin.py**

```python
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Category, Article, Tag

admin.site.register(Category, MPTTModelAdmin)
admin.site.register(Article)
admin.site.register(Tag)
```

**Step 3: マイグレーション + Commit**

```bash
python manage.py makemigrations wiki
python manage.py migrate
git add backend/wiki/models.py backend/wiki/admin.py && git commit -m "feat: add Category(MPTT), Article, Tag models"
```

---

### Task 1.4: DRF Serializers & ViewSets

**Objective:** REST API エンドポイント実装（Serializer + ViewSet + Router）

**Files:**
- Create: `backend/wiki/serializers.py`
- Create: `backend/wiki/views.py`
- Modify: `backend/wiki/urls.py` (create)
- Modify: `backend/config/urls.py`

**Step 1: serializers.py**

```python
from rest_framework import serializers
from .models import Category, Article, Tag


class TagSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'article_count']

    def get_article_count(self, obj):
        return obj.articles.count()


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'children', 'article_count']

    def get_children(self, obj):
        if obj.get_children().exists():
            return CategorySerializer(obj.get_children(), many=True).data
        return []

    def get_article_count(self, obj):
        return obj.articles.count()


class CategoryFlatSerializer(serializers.ModelSerializer):
    """フラットなカテゴリ一覧用（ツリー不要時）"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


class ArticleListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'category', 'category_name',
                  'tags', 'created_at', 'updated_at']


class ArticleDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'content', 'category', 'category_name',
                  'category_slug', 'tags', 'tag_ids', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tag_ids)
        return article

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tag_ids is not None:
            instance.tags.set(tag_ids)
        return instance
```

**Step 2: views.py**

```python
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Article, Tag
from .serializers import (
    CategorySerializer, CategoryFlatSerializer,
    ArticleListSerializer, ArticleDetailSerializer,
    TagSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            # ルートカテゴリのみを返し、children でツリー構築
            return CategorySerializer
        return CategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.filter(parent__isnull=True)
        return qs


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('category').prefetch_related('tags')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'content']
    ordering_fields = ['title', 'created_at', 'updated_at']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
```

**Step 3: wiki/urls.py**

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ArticleViewSet, TagViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

**Step 4: config/urls.py 修正**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('wiki.urls')),
]
```

**Step 5: Commit**

---

### Task 1.5: Vite React MPA プロジェクト初期化

**Objective:** Vite で MPA (Multi-Page Application) 構成の React プロジェクトを作成

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/article.html`
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/article.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/ArticlePage.jsx`

**Step 1: Dockerfile**

```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
```

**Step 2: package.json**

```json
{
  "name": "tech-wiki-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "mermaid": "^11.0.0",
    "highlight.js": "^11.10.0",
    "react-router-dom": "^7.0.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.0",
    "vite": "^6.0.0"
  }
}
```

**Step 3: vite.config.js (MPA設定)**

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: 'index.html',
        article: 'article.html',
      },
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
      },
    },
  },
});
```

**Step 4: ベース HTML (index.html / article.html)**

index.html (ホーム):
```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tech Wiki</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
```

article.html (記事詳細):
```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Article - Tech Wiki</title>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/article.jsx"></script>
</body>
</html>
```

**Step 5: 最小限の React エントリポイント**

src/main.jsx:
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

src/article.jsx:
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import ArticlePage from './ArticlePage';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ArticlePage />
  </React.StrictMode>
);
```

src/App.jsx:
```jsx
export default function App() {
  return <h1>Tech Wiki - Home</h1>;
}
```

src/ArticlePage.jsx:
```jsx
export default function ArticlePage() {
  return <h1>Article Page</h1>;
}
```

src/index.css:
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
```

**Step 6: npm install + Commit**

```bash
cd frontend && npm install
git add frontend/ && git commit -m "feat: scaffold Vite React MPA with 2 entry points"
```

---

### Task 1.6: Nginx 設定

**Objective:** Nginx のリバースプロキシ設定で CORS 回避

**Files:**
- Create: `nginx/nginx.conf`

```nginx
server {
    listen 80;
    server_name localhost;

    # Django REST API
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Django static (admin用)
    location /static/ {
        proxy_pass http://backend:8000;
    }

    # Vite Dev Server (frontend)
    location / {
        proxy_pass http://frontend:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Commit**

---

## Phase 2: バックエンド機能拡充

### Task 2.1: シードデータ投入 (management command)

**Objective:** 開発用のサンプルカテゴリ・タグ・記事を作成する management command

**Files:**
- Create: `backend/wiki/management/__init__.py`
- Create: `backend/wiki/management/commands/__init__.py`
- Create: `backend/wiki/management/commands/seed_data.py`

サンプル構造:
```
Category Tree:
  プログラミング
    ├── Python
    │   ├── Django
    │   └── FastAPI
    ├── JavaScript
    │   ├── React
    │   └── Node.js
    └── Go
  インフラ
    ├── Docker
    ├── Kubernetes
    └── AWS
  データベース
    ├── MySQL
    ├── PostgreSQL
    └── Redis
```

各カテゴリに1〜2個のMarkdown記事（mermaid図を含む）を投入。

**Step 1: seed_data.py**

```python
from django.core.management.base import BaseCommand
from wiki.models import Category, Tag, Article

CATEGORIES = {
    'プログラミング': {
        'Python': ['Django', 'FastAPI'],
        'JavaScript': ['React', 'Node.js'],
        'Go': [],
    },
    'インフラ': {
        'Docker': [],
        'Kubernetes': [],
        'AWS': [],
    },
    'データベース': {
        'MySQL': [],
        'PostgreSQL': [],
        'Redis': [],
    },
}

SAMPLE_ARTICLE = """# {title}

## 概要

{title}についての技術メモです。

## ポイント

- ポイント1
- ポイント2
- ポイント3

## コード例

```python
def hello():
    print("Hello, {title}!")
```

## アーキテクチャ図

```mermaid
graph TD
    A[クライアント] --> B[{title}]
    B --> C[データベース]
    B --> D[キャッシュ]
```

## 参考リンク

- [公式ドキュメント](https://example.com)
"""


class Command(BaseCommand):
    help = 'Seed database with sample categories, tags, and articles'

    def handle(self, *args, **options):
        # Create tags
        tags = {}
        for tag_name in ['入門', '中級', '上級', 'チートシート', 'トラブルシュート']:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags[tag_name] = tag

        # Create categories recursively
        def create_categories(tree, parent=None):
            for name, children in tree.items():
                cat, _ = Category.objects.get_or_create(
                    name=name, parent=parent,
                    defaults={'description': f'{name}に関する技術資料'}
                )
                # Create sample article
                Article.objects.get_or_create(
                    title=f'{name}入門ガイド',
                    category=cat,
                    defaults={'content': SAMPLE_ARTICLE.format(title=name)}
                )
                if children:
                    if isinstance(children, dict):
                        create_categories(children, cat)
                    else:
                        for child in children:
                            child_cat, _ = Category.objects.get_or_create(
                                name=child, parent=cat,
                                defaults={'description': f'{child}に関する技術資料'}
                            )
                            article, _ = Article.objects.get_or_create(
                                title=f'{child}の基礎',
                                category=child_cat,
                                defaults={'content': SAMPLE_ARTICLE.format(title=child)}
                            )
                            if child in ['入門', 'Django']:
                                article.tags.add(tags['入門'])
                            article.tags.add(tags['チートシート'])

        create_categories(CATEGORIES)
        self.stdout.write(self.style.SUCCESS('Seed data created successfully'))
```

**Step 2: Commit**

---

## Phase 3: フロントエンド実装

### Task 3.1: API クライアント層

**Objective:** API 通信用のユーティリティモジュール

**Files:**
- Create: `frontend/src/api/client.js`
- Create: `frontend/src/api/categories.js`
- Create: `frontend/src/api/articles.js`
- Create: `frontend/src/api/tags.js`

**Step 1: client.js (fetch ラッパー)**

```javascript
const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };
  const res = await fetch(url, config);
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  get: (url, params) => {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    return request(url + query);
  },
  post: (url, data) => request(url, { method: 'POST', body: JSON.stringify(data) }),
  put: (url, data) => request(url, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (url) => request(url, { method: 'DELETE' }),
};
```

**Step 2: categories.js / articles.js / tags.js**

```javascript
// categories.js
import { api } from './client';
export const fetchCategories = () => api.get('/categories/');

// articles.js
import { api } from './client';
export const fetchArticles = (params) => api.get('/articles/', params);
export const fetchArticle = (slug) => api.get(`/articles/${slug}/`);

// tags.js
import { api } from './client';
export const fetchTags = () => api.get('/tags/');
```

**Commit**

---

### Task 3.2: カテゴリツリーコンポーネント

**Objective:** 再帰的なツリー表示コンポーネント

**Files:**
- Create: `frontend/src/components/CategoryTree.jsx`
- Create: `frontend/src/components/CategoryTree.css`

**Step 1: CategoryTree.jsx**

```jsx
import { useState } from 'react';
import './CategoryTree.css';

function TreeNode({ node, level = 0, activeSlug, onSelect }) {
  const [expanded, setExpanded] = useState(level < 2);
  const hasChildren = node.children && node.children.length > 0;
  const isActive = activeSlug === node.slug;

  return (
    <li className="tree-node">
      <div
        className={`tree-item ${isActive ? 'active' : ''}`}
        style={{ paddingLeft: `${level * 16 + 8}px` }}
        onClick={() => {
          if (hasChildren) setExpanded(!expanded);
          onSelect(node.slug);
        }}
      >
        {hasChildren && (
          <span className={`tree-arrow ${expanded ? 'expanded' : ''}`}>▸</span>
        )}
        <span className="tree-icon">{hasChildren ? (expanded ? '📂' : '📁') : '📄'}</span>
        <span className="tree-name">{node.name}</span>
        {node.article_count > 0 && (
          <span className="tree-count">{node.article_count}</span>
        )}
      </div>
      {hasChildren && expanded && (
        <ul className="tree-children">
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              level={level + 1}
              activeSlug={activeSlug}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export default function CategoryTree({ categories, activeCategory, onSelectCategory }) {
  if (!categories || categories.length === 0) {
    return <div className="category-tree-empty">カテゴリがありません</div>;
  }
  return (
    <nav className="category-tree">
      <h3 className="tree-title">カテゴリ</h3>
      <ul className="tree-root">
        {categories.map((cat) => (
          <TreeNode
            key={cat.id}
            node={cat}
            activeSlug={activeCategory}
            onSelect={onSelectCategory}
          />
        ))}
      </ul>
    </nav>
  );
}
```

**Step 2: CategoryTree.css**

```css
.category-tree { padding: 16px 0; }
.tree-title { font-size: 14px; text-transform: uppercase; color: #888; padding: 0 16px 8px; }
.tree-root, .tree-children { list-style: none; }
.tree-item {
  display: flex; align-items: center; gap: 4px;
  padding: 6px 12px; cursor: pointer; border-radius: 4px; margin: 1px 4px;
  font-size: 14px; transition: background 0.15s;
}
.tree-item:hover { background: #f0f0f0; }
.tree-item.active { background: #e3f2fd; color: #1565c0; font-weight: 600; }
.tree-arrow { font-size: 10px; width: 12px; transition: transform 0.2s; }
.tree-arrow.expanded { transform: rotate(90deg); }
.tree-icon { font-size: 14px; }
.tree-name { flex: 1; }
.tree-count { background: #e0e0e0; color: #666; font-size: 11px; padding: 1px 6px; border-radius: 10px; }
.category-tree-empty { padding: 24px; text-align: center; color: #999; }
```

**Commit**

---

### Task 3.3: 記事一覧コンポーネント

**Objective:** 記事カード一覧表示

**Files:**
- Create: `frontend/src/components/ArticleList.jsx`
- Create: `frontend/src/components/ArticleList.css`

```jsx
import './ArticleList.css';

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ja-JP', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

export default function ArticleList({ articles, loading }) {
  if (loading) return <div className="article-list-loading">読み込み中...</div>;
  if (!articles || articles.length === 0) {
    return <div className="article-list-empty">記事がありません</div>;
  }

  return (
    <div className="article-list">
      {articles.map((article) => (
        <article key={article.id} className="article-card">
          <h3 className="article-card-title">
            <a href={`/article.html?slug=${article.slug}`}>{article.title}</a>
          </h3>
          <div className="article-card-meta">
            {article.category_name && (
              <span className="article-category">{article.category_name}</span>
            )}
            <span className="article-date">{formatDate(article.updated_at)}</span>
          </div>
          {article.tags && article.tags.length > 0 && (
            <div className="article-tags">
              {article.tags.map((tag) => (
                <span key={tag.id} className="tag">{tag.name}</span>
              ))}
            </div>
          )}
        </article>
      ))}
    </div>
  );
}
```

CSS:
```css
.article-list { display: flex; flex-direction: column; gap: 12px; padding: 16px; }
.article-card { border: 1px solid #e8e8e8; border-radius: 8px; padding: 16px; transition: box-shadow 0.2s; }
.article-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.article-card-title { font-size: 18px; margin-bottom: 8px; }
.article-card-title a { color: #1a1a1a; text-decoration: none; }
.article-card-title a:hover { color: #1565c0; }
.article-card-meta { display: flex; gap: 12px; font-size: 13px; color: #888; margin-bottom: 8px; }
.article-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.tag { background: #e8f5e9; color: #2e7d32; font-size: 12px; padding: 2px 8px; border-radius: 12px; }
.article-list-loading, .article-list-empty { padding: 48px; text-align: center; color: #999; }
```

**Commit**

---

### Task 3.4: 検索バーコンポーネント

**Objective:** 記事タイトル・本文検索

**Files:**
- Create: `frontend/src/components/SearchBar.jsx`
- Create: `frontend/src/components/SearchBar.css`

```jsx
import { useState } from 'react';
import './SearchBar.css';

export default function SearchBar({ onSearch }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="記事を検索..."
        className="search-input"
      />
      <button type="submit" className="search-button">🔍</button>
    </form>
  );
}
```

CSS:
```css
.search-bar { display: flex; padding: 12px 16px; border-bottom: 1px solid #e8e8e8; }
.search-input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px 0 0 6px; font-size: 14px; outline: none; }
.search-input:focus { border-color: #1565c0; }
.search-button { padding: 8px 16px; border: 1px solid #ddd; border-left: none; border-radius: 0 6px 6px 0; background: #f5f5f5; cursor: pointer; }
```

**Commit**

---

### Task 3.5: ホームページ (App.jsx) の統合

**Objective:** サイドバー（ツリー＋検索）＋記事一覧のレイアウト統合

**Files:**
- Modify: `frontend/src/App.jsx`
- Create: `frontend/src/App.css`

**Step 1: App.jsx**

```jsx
import { useState, useEffect, useCallback } from 'react';
import CategoryTree from './components/CategoryTree';
import ArticleList from './components/ArticleList';
import SearchBar from './components/SearchBar';
import { fetchCategories } from './api/categories';
import { fetchArticles } from './api/articles';
import './App.css';

export default function App() {
  const [categories, setCategories] = useState([]);
  const [articles, setArticles] = useState([]);
  const [activeCategory, setActiveCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCategories().then(setCategories).catch(console.error);
  }, []);

  const loadArticles = useCallback(async (params = {}) => {
    setLoading(true);
    try {
      const data = await fetchArticles(params);
      setArticles(data.results || data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // 初期ロード
  useEffect(() => {
    loadArticles();
  }, [loadArticles]);

  const handleCategorySelect = (slug) => {
    setActiveCategory(slug === activeCategory ? null : slug);
    if (slug && slug !== activeCategory) {
      loadArticles({ category__slug: slug });
    } else {
      loadArticles();
    }
  };

  const handleSearch = (query) => {
    loadArticles({ search: query });
  };

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <SearchBar onSearch={handleSearch} />
        <CategoryTree
          categories={categories}
          activeCategory={activeCategory}
          onSelectCategory={handleCategorySelect}
        />
      </aside>
      <main className="main-content">
        <header className="main-header">
          <h1>Tech Wiki</h1>
          <p className="main-subtitle">技術ナレッジベース</p>
        </header>
        <ArticleList articles={articles} loading={loading} />
      </main>
    </div>
  );
}
```

**Step 2: App.css**

```css
.app-layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 280px; min-width: 280px; border-right: 1px solid #e8e8e8;
  background: #fafafa; overflow-y: auto;
}
.main-content { flex: 1; overflow-y: auto; }
.main-header { padding: 24px 16px 16px; border-bottom: 1px solid #e8e8e8; }
.main-header h1 { font-size: 24px; font-weight: 700; }
.main-subtitle { font-size: 14px; color: #888; margin-top: 4px; }
```

**Commit**

---

### Task 3.6: Markdown レンダリングコンポーネント

**Objective:** react-markdown + remark-gfm + mermaid を使った Markdown 表示

**Files:**
- Create: `frontend/src/components/MarkdownRenderer.jsx`
- Create: `frontend/src/components/MarkdownRenderer.css`
- Create: `frontend/src/components/MermaidBlock.jsx`

**Step 1: MermaidBlock.jsx** (mermaid図のレンダリング)

```jsx
import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
});

export default function MermaidBlock({ chart }) {
  const ref = useRef(null);
  const id = `mermaid-${Math.random().toString(36).slice(2, 9)}`;

  useEffect(() => {
    if (ref.current) {
      mermaid.render(id, chart).then(({ svg }) => {
        if (ref.current) {
          ref.current.innerHTML = svg;
        }
      }).catch((err) => {
        if (ref.current) {
          ref.current.innerHTML = `<pre class="mermaid-error">Mermaid render error: ${err.message}</pre>`;
        }
      });
    }
  }, [chart, id]);

  return <div ref={ref} className="mermaid-block" />;
}
```

**Step 2: MarkdownRenderer.jsx**

```jsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MermaidBlock from './MermaidBlock';
import hljs from 'highlight.js';
import { useEffect } from 'react';
import './MarkdownRenderer.css';
import 'highlight.js/styles/github.css';

export default function MarkdownRenderer({ content }) {
  useEffect(() => {
    // highlight.js をコードブロックに適用
    document.querySelectorAll('.markdown-body pre code').forEach((block) => {
      hljs.highlightElement(block);
    });
  });

  return (
    <div className="markdown-body">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, inline, className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const codeStr = String(children).replace(/\n$/, '');

            if (!inline && match && match[1] === 'mermaid') {
              return <MermaidBlock chart={codeStr} />;
            }

            if (!inline && match) {
              return (
                <pre className={className}>
                  <code className={className} {...props}>
                    {codeStr}
                  </code>
                </pre>
              );
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
```

**Step 3: MarkdownRenderer.css**

```css
.markdown-body {
  font-size: 16px; line-height: 1.8; color: #333;
  max-width: 860px; margin: 0 auto; padding: 32px 24px;
}
.markdown-body h1 { font-size: 2em; margin: 0.67em 0; border-bottom: 2px solid #e8e8e8; padding-bottom: 0.3em; }
.markdown-body h2 { font-size: 1.5em; margin: 1em 0 0.5em; border-bottom: 1px solid #eee; padding-bottom: 0.2em; }
.markdown-body h3 { font-size: 1.25em; margin: 0.8em 0 0.4em; }
.markdown-body p { margin: 0.8em 0; }
.markdown-body ul, .markdown-body ol { padding-left: 2em; margin: 0.8em 0; }
.markdown-body li { margin: 0.3em 0; }
.markdown-body pre { background: #f6f8fa; border-radius: 6px; padding: 16px; overflow-x: auto; margin: 1em 0; }
.markdown-body code { font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 0.9em; }
.markdown-body :not(pre) > code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
.markdown-body table { border-collapse: collapse; width: 100%; margin: 1em 0; }
.markdown-body th, .markdown-body td { border: 1px solid #ddd; padding: 8px 12px; text-align: left; }
.markdown-body th { background: #f6f8fa; font-weight: 600; }
.markdown-body blockquote { border-left: 4px solid #ddd; padding-left: 16px; color: #666; margin: 1em 0; }
.markdown-body img { max-width: 100%; }
.markdown-body a { color: #1565c0; }
.mermaid-block { display: flex; justify-content: center; margin: 1.5em 0; overflow-x: auto; }
.mermaid-error { color: #d32f2f; background: #ffebee; padding: 12px; border-radius: 6px; }
```

**Commit**

---

### Task 3.7: 記事詳細ページ (ArticlePage.jsx)

**Objective:** 記事スラッグからAPI取得しMarkdownレンダリング

**Files:**
- Modify: `frontend/src/ArticlePage.jsx`
- Create: `frontend/src/ArticlePage.css`

```jsx
import { useState, useEffect } from 'react';
import MarkdownRenderer from './components/MarkdownRenderer';
import { fetchArticle } from './api/articles';
import './ArticlePage.css';

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('ja-JP', {
    year: 'numeric', month: 'long', day: 'numeric',
  });
}

export default function ArticlePage() {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');
    if (!slug) {
      setError('記事が指定されていません');
      setLoading(false);
      return;
    }

    fetchArticle(slug)
      .then((data) => {
        setArticle(data);
        document.title = `${data.title} - Tech Wiki`;
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="article-loading">読み込み中...</div>;
  if (error) return <div className="article-error">{error}</div>;
  if (!article) return <div className="article-error">記事が見つかりません</div>;

  return (
    <div className="article-page">
      <header className="article-header">
        <div className="article-nav-top">
          <a href="/" className="back-link">← ホームに戻る</a>
          {article.category_name && (
            <span className="breadcrumb">
              <a href={`/?category=${article.category_slug}`}>{article.category_name}</a>
            </span>
          )}
        </div>
        <h1 className="article-title">{article.title}</h1>
        <div className="article-meta">
          <span>更新: {formatDate(article.updated_at)}</span>
          <span>作成: {formatDate(article.created_at)}</span>
        </div>
        {article.tags && article.tags.length > 0 && (
          <div className="article-tags">
            {article.tags.map((tag) => (
              <span key={tag.id} className="tag">{tag.name}</span>
            ))}
          </div>
        )}
      </header>
      <MarkdownRenderer content={article.content} />
    </div>
  );
}
```

CSS:
```css
.article-page { max-width: 900px; margin: 0 auto; padding: 16px; }
.article-header { margin-bottom: 24px; }
.article-nav-top { display: flex; gap: 16px; margin-bottom: 16px; font-size: 14px; }
.back-link { color: #1565c0; text-decoration: none; }
.breadcrumb a { color: #888; text-decoration: none; }
.article-title { font-size: 2em; font-weight: 700; margin-bottom: 8px; }
.article-meta { display: flex; gap: 16px; font-size: 14px; color: #888; margin-bottom: 12px; }
.article-tags { display: flex; gap: 6px; flex-wrap: wrap; }
.article-loading, .article-error { padding: 80px 24px; text-align: center; font-size: 18px; color: #888; }
.article-error { color: #d32f2f; }
```

**Commit**

---

## Phase 4: Docker 起動確認と統合テスト

### Task 4.1: Docker Compose 起動確認

**Objective:** 全サービスの起動と疎通確認

```bash
# プロジェクトルートで
docker compose up -d

# DB 起動待ち
sleep 15

# Django マイグレーション
docker compose exec backend python manage.py migrate

# シードデータ投入
docker compose exec backend python manage.py seed_data

# 確認
curl http://localhost/api/categories/
curl http://localhost/api/articles/
curl http://localhost/              # フロントの HTML
```

**Commit**

---

### Task 4.2: README.md 作成

**Objective:** プロジェクト概要と開発手順をドキュメント化

**Files:**
- Create: `README.md`

内容: アーキテクチャ概要、起動手順、API一覧、ディレクトリ構造
