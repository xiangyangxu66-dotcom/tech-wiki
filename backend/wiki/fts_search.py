"""
FTS5 full-text search filter backend for SQLite.
Supports:
  - ?search_title=      → title column FTS5
  - ?search_content=    → content REGEXP (always; whitespace → AND)
  - ?search=            → combined title+content FTS5 (backward compat)
  - Both title+content  → AND (intersect)
  - bm25 ranking with column weights (title=10.0, content=1.0)

search_content whitespace handling:
  Split on any Unicode whitespace (ASCII space, CJK fullwidth U+3000,
  tab, newline, etc.).  Each token becomes a REGEXP AND condition.
  Example: "docker 　 compose" → content REGEXP 'docker' AND content REGEXP 'compose'
"""

import re
from django.db import connection
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request

# Characters with special meaning in FTS5 MATCH expressions.
# Escaped by doubling (FTS5 convention).
_FTS5_SPECIAL = set('*"^()-+:[]{}')

# Regexp to split on any Unicode whitespace (\s with re.UNICODE covers
# ASCII space, CJK fullwidth U+3000, tab, etc.)
_SPLIT_RE = re.compile(r'\s+')

# | with whitespace on at least one side → OR separator.
# Without ANY surrounding whitespace, | stays as regex literal (e.g. "docker|k8s").
# Covers all four cases:
#   "docker | k8s"   → OR (space both sides)
#   "docker |k8s"    → OR (space before only)
#   "docker| k8s"    → OR (space after only)
#   "docker|k8s"     → regex alternation literal
_OR_SPLIT_RE = re.compile(r'(?:\s+\||\|\s+)')


def _escape_fts5(term: str) -> str:
    """Escape a single search term for FTS5 MATCH."""
    return "".join(ch * 2 if ch in _FTS5_SPECIAL else ch for ch in term)


def _build_column_query(term: str, column: str) -> str:
    """Build FTS5 column-prefixed prefix query: title:Docker*

    Uses prefix matching (bare term + *) instead of phrase matching ("term")
    because FTS5 with unicode61 tokenizer treats ASCII+CJK mixed strings
    (e.g. 'Docker入門') as a single token. Column-prefixed phrase queries
    (title:"Docker") don't match single-token 'docker入門'.
    """
    escaped = _escape_fts5(term)
    return f'{column}:{escaped}*'


def _run_fts5_search(table: str, match_expr: str) -> list[int]:
    """Execute FTS5 query with bm25 ranking. Returns ordered list of row IDs."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"""
            SELECT {table}.id
            FROM {table}_fts
            JOIN {table} ON {table}_fts.rowid = {table}.id
            WHERE {table}_fts MATCH %s
            ORDER BY bm25({table}_fts, 10.0, 1.0)
            """,
            [match_expr],
        )
        return [row[0] for row in cursor.fetchall()]


def _run_regexp_search(table: str, or_groups: list[list[str]]) -> list[int]:
    """Execute SQLite REGEXP on content with OR-of-ANDs semantics.

    Each sub-list is an AND group — all terms within must match.
    Different groups are OR-ed (union, deduplicated).

    Example:
      or_groups = [["docker", "compose"], ["kubernetes"]]
      → (content REGEXP 'docker' AND content REGEXP 'compose') OR (content REGEXP 'kubernetes')

    Invalid regex (e.g. unbalanced bracket "[rasa") is silently skipped;
    valid groups still return results.

    Returns deduplicated ordered list of row IDs (by updated_at DESC).
    """
    if not or_groups:
        return []
    with connection.cursor() as cursor:
        seen: set[int] = set()
        result: list[int] = []
        for group in or_groups:
            if not group:
                continue
            conditions = " AND ".join([f"{table}.content REGEXP '(?i)' || %s" for _ in group])
            try:
                cursor.execute(
                    f"""
                    SELECT {table}.id
                    FROM {table}
                    WHERE {conditions}
                    ORDER BY {table}.updated_at DESC
                    """,
                    group,
                )
                for row in cursor.fetchall():
                    rid: int = row[0]
                    if rid not in seen:
                        seen.add(rid)
                        result.append(rid)
            except Exception:
                # Invalid regex pattern (unbalanced bracket, etc.) →
                # skip this OR group, continue with others
                continue
        return result


class FTS5SearchFilter(BaseFilterBackend):
    """Full-text search using SQLite FTS5 + REGEXP.

    Query parameters:
        search_title   — FTS5 on title column
        search_content — REGEXP on content (whitespace → AND)
        search         — combined FTS5 on title+content (backward compat)

    Priority: new params > legacy `search`. Title + content = AND (INTERSECT).
    """

    def filter_queryset(self, request: Request, queryset, view):
        model = queryset.model
        table = model._meta.db_table

        title_term = (request.query_params.get("search_title") or "").strip()
        content_raw = (request.query_params.get("search_content") or "").strip()
        legacy_search = (request.query_params.get("search") or "").strip()

        # Split by `|` (with surrounding whitespace) → OR groups.
        # Within each group, split on whitespace → AND terms.
        # "docker compose | kubernetes" → [["docker","compose"], ["kubernetes"]]
        # "docker|kubernetes"          → [["docker|kubernetes"]]  (regex OR literal)
        content_groups: list[list[str]] = []
        if content_raw:
            for part in _OR_SPLIT_RE.split(content_raw):
                words = [w for w in _SPLIT_RE.split(part) if w]
                if words:
                    content_groups.append(words)

        # --- Regexp path (content always uses REGEXP) ---
        if content_groups:
            matched_ids = _run_regexp_search(table, content_groups)
            if title_term:
                # AND with title FTS5
                title_expr = _build_column_query(title_term, "title")
                title_ids = _run_fts5_search(table, title_expr)
                title_set = set(title_ids)
                matched_ids = [i for i in matched_ids if i in title_set]
            if not matched_ids:
                return queryset.none()
            return self._order_by_ids(queryset, matched_ids)

        # --- FTS5 path (title only, or legacy combined) ---
        clauses = []
        if title_term:
            clauses.append(_build_column_query(title_term, "title"))
        if legacy_search and not title_term:
            # Legacy: search both columns
            escaped = _escape_fts5(legacy_search)
            clauses.append(f'("{escaped}")')

        if not clauses:
            return queryset  # no search params → pass through

        match_expr = " ".join(clauses)
        matched_ids = _run_fts5_search(table, match_expr)

        if not matched_ids:
            return queryset.none()

        return self._order_by_ids(queryset, matched_ids)

    @staticmethod
    def _order_by_ids(queryset, ordered_ids: list[int]):
        """Preserve FTS5 bm25 ranking in Django queryset."""
        from django.db.models import Case, When

        whens = [When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)]
        return queryset.filter(id__in=ordered_ids).order_by(Case(*whens))


def split_search_words(raw: str) -> list[str]:
    """Split raw search input on any Unicode whitespace, returning non-empty tokens."""
    return [w for w in _SPLIT_RE.split(raw.strip()) if w]
