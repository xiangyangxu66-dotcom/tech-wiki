import hashlib
import re
import yaml
from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

HASH_LEN = 16  # MD5 先頭16桁で十分


def _slugify_with_fallback(name, prefix=''):
    """slugify() strips non-ASCII (e.g. Japanese) → fallback to MD5 hash."""
    s = slugify(name)
    if s:
        return s
    return f'{prefix}{hashlib.md5(name.encode()).hexdigest()[:8]}'


FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)


def parse_frontmatter(content: str):
    """YAML frontmatter をパース。見つからなければ (None, content) を返す。"""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    body = content[m.end():]
    return fm, body


# HackMD-style inline tags: ###### tags: `auth` `saml`
# 行番号接頭辞 (例: "   399|") にも対応
HACKMD_TAGS_RE = re.compile(
    r'^\s*(?:\d+\|\s*)*#{1,6}\s*tags:\s*(`.+?`[\s,]*)+$', re.MULTILINE | re.IGNORECASE
)


def contains_mermaid(content: str) -> bool:
    """Markdown 内に Mermaid fenced code block があるかを判定。"""
    return '```mermaid' in content.lower()

def extract_tags_from_content(content: str):
    """content からタグを抽出。優先順:
    1. YAML frontmatter tags
    2. HackMD 形式 `###### tags: `tag1` `tag2``
    """
    fm, body = parse_frontmatter(content)
    if fm:
        raw_tags = fm.get('tags', [])
        if not raw_tags:
            raw_tags = fm.get('tag', [])      # singular variant
        if raw_tags:
            if isinstance(raw_tags, str):
                raw_tags = [t.strip() for t in raw_tags.split(',')]
            tags = [str(t).strip() for t in raw_tags if str(t).strip()]
            if tags:
                return tags

    # HackMD 形式をスキャン
    m = HACKMD_TAGS_RE.search(content)
    if m:
        # バッククォート内の文字列を抽出
        tags = re.findall(r'`([^`]+)`', m.group(0))
        return [t.strip() for t in tags if t.strip()]

    return []


# ============================================================================
# Category（カテゴリ）— MPTT ツリー構造
# ============================================================================
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
            self.slug = _slugify_with_fallback(self.name, 'cat-')
        super().save(*args, **kwargs)


# ============================================================================
# Note（技術ノート）— タグは content のフロントマターから抽出
# ============================================================================
class Note(models.Model):
    class Status(models.TextChoices):
        DRAFT     = 'draft',     '下書き'
        PUBLISHED = 'published', '整理済'

    title      = models.CharField(max_length=500)
    slug       = models.SlugField(max_length=255, unique=True)
    content    = models.TextField()                           # Markdown 本文（DB格納）
    note_tags  = models.JSONField(default=list, blank=True)    # タグ文字列配列（フロントマター由来）
    category   = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='notes'
    )
    content_hash = models.CharField(max_length=HASH_LEN, default='', blank=True)  # MD5 先頭16桁（重複検知）
    has_mermaid  = models.BooleanField(default=False, db_index=True)
    bookmark     = models.BooleanField(default=False)            # ブックマーク（最上位表示）
    status       = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-bookmark', '-updated_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['bookmark']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['title']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slugify_with_fallback(self.title, 'note-')
        # ★ content のフロントマターからタグを自動抽出
        self.note_tags = extract_tags_from_content(self.content)
        # ★ content の MD5 hash を先頭16桁で保持（重複検知）
        self.content_hash = hashlib.md5(self.content.encode()).hexdigest()[:HASH_LEN]
        # ★ Mermaid fenced code block の有無を保持（描画最適化用）
        self.has_mermaid = contains_mermaid(self.content)
        super().save(*args, **kwargs)


# ============================================================================
# AuditLog（監査ログ）— 操作履歴
# ============================================================================
class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', '作成'
        UPDATE = 'UPDATE', '更新'
        VIEW   = 'VIEW',   '閲覧'

    user       = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    username   = models.CharField(max_length=150, default='')
    action     = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=100)
    object_id  = models.BigIntegerField()
    summary    = models.CharField(max_length=500, default='')
    detail     = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['action']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} {self.model_name}#{self.object_id} by {self.username}'


# ============================================================================
# SystemConfig（動的設定）
# ============================================================================
class SystemConfig(models.Model):
    key         = models.CharField(max_length=200, unique=True)
    value       = models.TextField()
    description = models.TextField(blank=True, default='')
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['key']

    def __str__(self):
        return f'{self.key} = {self.value[:50]}'
