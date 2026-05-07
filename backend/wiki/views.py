from __future__ import annotations

from rest_framework import viewsets, filters, mixins
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.db import connections
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tag, Category, Note, AuditLog, SystemConfig
from .fts_search import FTS5SearchFilter
import time

# Process start time for uptime tracking
_PROCESS_START = time.monotonic()


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@api_view(['GET'])
def health_check(request):
    """Basic health: DB接続確認。Docker healthcheck用。"""
    try:
        connections['default'].cursor()
        db_ok = True
    except Exception:
        db_ok = False
    status_code = 200 if db_ok else 503
    return Response({'status': 'ok' if db_ok else 'degraded', 'db': db_ok}, status=status_code)


@api_view(['GET'])
def health_detailed(request):
    """Detailed health: Admin only (TODO: auth check)。"""
    statuses = {}
    # DB
    try:
        connections['default'].cursor()
        statuses['db'] = 'ok'
    except Exception as e:
        statuses['db'] = f'error: {e}'

    # Uptime
    statuses['uptime_seconds'] = int(time.monotonic() - _PROCESS_START)

    # Counts
    statuses['notes'] = Note.objects.count()
    statuses['categories'] = Category.objects.count()

    all_ok = all(v == 'ok' or isinstance(v, int) for v in statuses.values())
    return Response({'status': 'ok' if all_ok else 'degraded', 'details': statuses})


# ---------------------------------------------------------------------------
# タグ集計（SQL GROUP BY）
# ---------------------------------------------------------------------------
@api_view(['GET'])
def tag_aggregation(request):
    """Tag テーブルから COUNT 集計。無所属カウントも返す。

    クエリパラメータ ?min_count=N で最小カウントフィルタ（デフォルト1）。
    """
    min_count = int(request.query_params.get('min_count', 1))
    result = list(
        Tag.objects
        .annotate(note_count=Count('notes'))
        .filter(note_count__gte=min_count)
        .values('name', 'slug', 'note_count')
        .order_by('-note_count', 'name')
    )
    # rename note_count → count for frontend compatibility
    result = [{'name': r['name'], 'slug': r['slug'], 'count': r['note_count']} for r in result]

    # 無所属
    untagged = Note.objects.filter(tags__isnull=True).count()
    if untagged > 0:
        result.append({'name': '無所属', 'count': untagged})
    return Response(result)


# ---------------------------------------------------------------------------
# タグ一覧（エディタ補完用）
# ---------------------------------------------------------------------------
@api_view(['GET'])
def tag_list(request):
    """全タグの name + slug 一覧。エディタのタグ補完・選択用。"""
    data = list(Tag.objects.values('name', 'slug').order_by('name'))
    return Response(data)


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']

    def get_serializer_class(self):
        from .serializers import RecursiveCategorySerializer
        return RecursiveCategorySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            return qs.filter(parent__isnull=True)
        return qs


# ---------------------------------------------------------------------------
# Note
# ---------------------------------------------------------------------------
class NoteViewSet(viewsets.ModelViewSet):
    """
    Note CRUD。

    クエリパラメータ:
      ?tag=タグslug           → tags M2M を絞り込み
      ?category__slug=xxx     → カテゴリ絞り込み
      ?status=published       → 公開済のみ
      ?bookmark=1             → ブックマークのみ
      ?search_title=キーワード  → タイトル FTS5 全文検索
      ?search_content=正規表現  → 本文 REGEXP 検索（空白区切り=AND）
      ?search=キーワード       → タイトル+本文 統合 FTS5（後方互換）
    """
    queryset = Note.objects.select_related('category').prefetch_related('tags').order_by('-bookmark', '-updated_at')
    filter_backends = [DjangoFilterBackend, FTS5SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'status', 'bookmark']
    ordering_fields = ['title', 'created_at', 'updated_at']
    ordering = ['-bookmark', '-updated_at']
    lookup_field = 'slug'

    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        from .serializers import NoteListSerializer, NoteDetailSerializer
        if self.action == 'list':
            return NoteListSerializer
        return NoteDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        tag_slug = self.request.query_params.get('tag')
        if tag_slug == '無所属':
            qs = qs.filter(tags__isnull=True)
        elif tag_slug:
            qs = qs.filter(tags__slug=tag_slug)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        snippets = self._build_snippets(page) if page is not None else {}
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
            context={'_snippets': snippets},
        )
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def _build_snippets(self, page):
        """Build snippets for list results when search params are active.

        Two paths:
          1. Title search (FTS5) → SQLite snippet() with <mark> wrappers.
          2. Content only (REGEXP) → Python snippet with regex match window.
          3. Both → REGEXP (content) snippet takes priority.
        """
        params = self.request.query_params
        title = (params.get('search_title') or '').strip()
        content = (params.get('search_content') or '').strip()
        legacy = (params.get('search') or '').strip() if not (title or content) else ''

        if not title and not content and not legacy:
            return {}

        from .fts_search import _escape_fts5, _build_column_query, _OR_SPLIT_RE, _SPLIT_RE

        # --- Path 1: FTS5 snippet (title or legacy search) ---
        fts5_expr = ''
        if title:
            fts5_expr = _build_column_query(title, 'title')
        elif legacy:
            fts5_expr = f'("{_escape_fts5(legacy)}")'

        if fts5_expr and not content:
            from django.db import connection
            snippets = {}
            with connection.cursor() as cursor:
                for note in page:
                    cursor.execute(
                        """SELECT snippet(wiki_note_fts, -1, '<mark>', '</mark>', '…', 48)
                           FROM wiki_note_fts
                           WHERE wiki_note_fts MATCH %s AND rowid = %s""",
                        [fts5_expr, note.id],
                    )
                    row = cursor.fetchone()
                    if row and row[0]:
                        snippets[note.id] = row[0]
            return snippets

        # --- Path 2: REGEXP snippet (content-only search) ---
        if not content:
            return {}

        # Split content into OR-of-ANDs groups (same as fts_search.py)
        content_groups: list[list[str]] = []
        for part in _OR_SPLIT_RE.split(content):
            words = [w for w in _SPLIT_RE.split(part) if w]
            if words:
                content_groups.append(words)

        if not content_groups:
            return {}

        import re as _re
        PAGE_SNIPPET_WINDOW = 160  # chars around first match

        snippets = {}
        for note in page:
            if not note.content:
                continue
            text = note.content
            snippet = self._regexp_snippet(text, content_groups, PAGE_SNIPPET_WINDOW)
            if snippet:
                snippets[note.id] = snippet
        return snippets

    @staticmethod
    def _regexp_snippet(text: str, or_groups: list[list[str]], window: int) -> str | None:
        """Build a snippet window from text, highlighting regex matches with <mark>.

        or_groups: list of AND groups, e.g. [['docker','compose'], ['kubernetes']]
        Each term in a group becomes a regex pattern (AND within group, OR across groups).
        """
        import re as _re

        # Search each OR group: find the earliest group where ALL terms match.
        min_start = len(text)
        max_end = 0
        matched_terms: set[str] = set()
        found_any = False

        for group in or_groups:
            group_start = len(text)
            group_end = 0
            all_found = True
            group_terms: set[str] = set()
            for term in group:
                m = _re.search(_re.escape(term), text, _re.IGNORECASE)
                if not m:
                    all_found = False
                    break
                group_start = min(group_start, m.start())
                group_end = max(group_end, m.end())
                group_terms.add(term)
            if all_found:
                found_any = True
                if group_start < min_start:
                    min_start = group_start
                    max_end = group_end
                matched_terms |= group_terms

        if not found_any:
            return None

        # Window around the earliest match
        half = window // 2
        start = max(0, min_start - half)
        end = min(len(text), max_end + half)
        snippet = text[start:end]

        prefix = '…' if start > 0 else ''
        suffix = '…' if end < len(text) else ''

        # Highlight all matched terms in the snippet
        for term in matched_terms:
            snippet = _re.sub(
                _re.escape(term),
                lambda m: f'<mark>{m.group(0)}</mark>',
                snippet,
                flags=_re.IGNORECASE,
            )

        return f'{prefix}{snippet}{suffix}'

    @action(detail=True, methods=['post'])
    def toggle_bookmark(self, request, slug=None):
        note = self.get_object()
        note.bookmark = not note.bookmark
        note.save(update_fields=['bookmark', 'updated_at'])
        serializer = self.get_serializer(note)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# AuditLog — ReadOnly
# ---------------------------------------------------------------------------
class AuditLogViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        from .serializers import AuditLogSerializer
        return AuditLogSerializer


# ---------------------------------------------------------------------------
# SystemConfig — ReadOnly
# ---------------------------------------------------------------------------
class SystemConfigViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SystemConfig.objects.all()

    def get_serializer_class(self):
        from .serializers import SystemConfigSerializer
        return SystemConfigSerializer
