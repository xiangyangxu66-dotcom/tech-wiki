"""
search_content / search_title / search の FTS5 + REGEXP 統合テスト。

カバーするパターン:
  - search_content: 単語 / AND / OR (|) / 全角空白 / メタキャラ / 不正regex
  - search_title: FTS5
  - 複合 (title + content AND)
  - スニペット (REGEXP Mark / FTS5 Mark)
"""
from __future__ import annotations

import pytest
from django.urls import reverse
from wiki.models import Category, Note


_cat_counter = 0


def _make_cat(**kw):
    global _cat_counter
    _cat_counter += 1
    defaults = {
        'name': f'検索テスト{_cat_counter}',
        'slug': f'search-test-{_cat_counter}',
    }
    defaults.update(kw)
    return Category.objects.create(**defaults)


_note_counter = 0


def _make_note(title, content, cat=None, **kw):
    """検索テスト用ノート作成ユーティリティ。"""
    global _note_counter
    _note_counter += 1
    defaults = {
        'title': title,
        'slug': f'{title.lower().replace(" ", "-")}-{_note_counter}',
        'content': content,
        'category': cat or _make_cat(),
        'status': Note.Status.PUBLISHED,
    }
    defaults.update(kw)
    return Note.objects.create(**defaults)


# ═══════════════════════════════════════════════════════════════════
# search_content — REGEXP
# ═══════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSearchContent:
    """?search_content= の REGEXP 検索パターン全網羅。"""

    # ── 単語 ──

    def test_single_word_match(self, api_client):
        _make_note('Docker入門', '# Docker\n\nコンテナオーケストレーション。')
        _make_note('Kubernetes入門', '# Kubernetes\n\nPodとService。')
        url = reverse('note-list') + '?search_content=Docker'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        assert resp.data['results'][0]['title'] == 'Docker入門'

    def test_single_word_no_match(self, api_client):
        _make_note('Docker入門', '# Docker')
        url = reverse('note-list') + '?search_content=存在しない言葉'
        resp = api_client.get(url)
        assert resp.data['count'] == 0

    # ── AND（空白区切り） ──

    def test_and_both_match(self, api_client):
        _make_note('A', 'docker compose でデプロイ。')
        _make_note('B', 'docker のみ。')
        url = reverse('note-list') + '?search_content=docker compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        assert resp.data['results'][0]['title'] == 'A'

    def test_and_partial_no_match(self, api_client):
        _make_note('A', 'docker だけ。')
        url = reverse('note-list') + '?search_content=docker kubernetes'
        resp = api_client.get(url)
        assert resp.data['count'] == 0

    def test_and_case_insensitive(self, api_client):
        _make_note('A', 'Docker Compose')
        url = reverse('note-list') + '?search_content=docker compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    def test_and_three_terms(self, api_client):
        _make_note('A', 'Apple Banana Cherry')
        _make_note('B', 'Apple Banana')
        url = reverse('note-list') + '?search_content=Apple Banana Cherry'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    # ── OR（| 前後に空白） ──

    def test_or_both_sides_space(self, api_client):
        _make_note('A', 'docker の話。')
        _make_note('B', 'kubernetes の話。')
        _make_note('C', '無関係。')
        url = reverse('note-list') + '?search_content=docker | kubernetes'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_or_space_before_only(self, api_client):
        """'docker |k8s' → OR: 'docker' と 'k8s'"""
        _make_note('A', 'docker の話。')
        _make_note('B', 'k8s の話。')
        url = reverse('note-list') + '?search_content=docker |k8s'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_or_space_after_only(self, api_client):
        """'docker| k8s' → OR: 'docker' と 'k8s'"""
        _make_note('A', 'docker の話。')
        _make_note('B', 'k8s の話。')
        url = reverse('note-list') + '?search_content=docker| k8s'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_or_one_side_empty(self, api_client):
        """片側だけヒット → その側の結果を返す"""
        _make_note('A', 'docker の話。')
        _make_note('B', '無関係。')
        url = reverse('note-list') + '?search_content=docker | 存在しない'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    # ── | 空白なし → 正規表現リテラル ──

    def test_no_space_around_pipe_is_regex_alternation(self, api_client):
        """'docker|k8s' は正規表現の OR → docker または k8s を含む行にマッチ"""
        _make_note('A', 'docker の話。')
        _make_note('B', 'k8s の話。')
        _make_note('C', '無関係。')
        url = reverse('note-list') + '?search_content=docker|k8s'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_regex_alternation_matches_partial(self, api_client):
        """'dock|kube' → docker か kubernetes の一部にマッチ"""
        _make_note('A', 'docker')
        _make_note('B', 'kubernetes')
        url = reverse('note-list') + '?search_content=dock|kube'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    # ── CJK 全角空白 (U+3000) ──

    def test_cjk_fullwidth_space_and(self, api_client):
        """全角空白も AND 区切りとして扱う"""
        _make_note('A', 'docker compose の設定。')
        _make_note('B', 'docker のみ。')
        url = reverse('note-list') + '?search_content=docker\u3000compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    # ── 正規表現メタキャラ ──

    def test_regex_dot_wildcard(self, api_client):
        """. は任意の1文字にマッチ（REGEXP）"""
        _make_note('A', 'docker')
        _make_note('B', 'docksr')
        url = reverse('note-list') + '?search_content=dock.r'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_regex_star_quantifier(self, api_client):
        """* は直前要素の0回以上繰り返し"""
        _make_note('A', 'test')
        _make_note('B', 'tesst')
        _make_note('C', 'tessst')
        url = reverse('note-list') + '?search_content=tes*t'
        resp = api_client.get(url)
        # tes*t matches: test (s×0), tesst (s×2), tessst (s×3) → all 3
        # teeest does NOT match because eee is not s*
        assert resp.data['count'] == 3

    def test_regex_plus_quantifier(self, api_client):
        """+ は直前要素の1回以上"""
        _make_note('A', 'test')
        _make_note('B', 'tesst')
        url = reverse('note-list') + '?search_content=tes+t'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    def test_regex_caret_anchor(self, api_client):
        """^ は行頭"""
        _make_note('A', 'docker compose up')
        _make_note('B', 'run docker compose')
        url = reverse('note-list') + '?search_content=^docker'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    def test_regex_dollar_anchor(self, api_client):
        """$ は行末"""
        _make_note('A', 'end with docker')
        _make_note('B', 'docker end')
        url = reverse('note-list') + '?search_content=docker$'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    def test_regex_bracket_class(self, api_client):
        """[abc] は文字クラス"""
        _make_note('A', 'cat')
        _make_note('B', 'bat')
        _make_note('C', 'rat')
        url = reverse('note-list') + '?search_content=[cb]at'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    # ── 不正な正規表現（graceful エラーハンドリング） ──

    def test_invalid_regex_graceful(self, api_client):
        """未対応の [ はエラーにならず空結果を返す"""
        _make_note('A', 'test [unbalanced')
        # [unbalanced は不正正規表現 → fts_search.py で try/except されスキップ
        url = reverse('note-list') + '?search_content=[unbalanced'
        resp = api_client.get(url)
        assert resp.status_code == 200
        assert resp.data['count'] == 0

    # ── 複合 OR + AND ──

    def test_or_of_and_groups(self, api_client):
        """'docker compose | kubernetes pod' → (docker AND compose) OR (kubernetes AND pod)"""
        _make_note('A', 'docker compose で構築。')
        _make_note('B', 'kubernetes pod の管理。')
        _make_note('C', 'docker だけ。')
        _make_note('D', '無関係。')
        url = reverse('note-list') + '?search_content=docker compose | kubernetes pod'
        resp = api_client.get(url)
        assert resp.data['count'] == 2

    # ── 日本語 ──

    def test_japanese_text(self, api_client):
        _make_note('A', 'コンテナオーケストレーションの話。')
        _make_note('B', '関係ない。')
        url = reverse('note-list') + '?search_content=コンテナ'
        resp = api_client.get(url)
        assert resp.data['count'] == 1

    # ── 中国語 ──

    def test_chinese_text(self, api_client):
        _make_note('A', '容器编排与调度。')
        _make_note('B', '无关。')
        url = reverse('note-list') + '?search_content=编排'
        resp = api_client.get(url)
        assert resp.data['count'] == 1


# ═══════════════════════════════════════════════════════════════════
# search_title — FTS5
# ═══════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSearchTitle:
    """?search_title= の FTS5 タイトル検索。"""

    def test_exact_match(self, api_client):
        _make_note('Docker Compose 実践入門', '# 本文')
        _make_note('Kubernetes Pod 設計', '# 本文')
        url = reverse('note-list') + '?search_title=Docker'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        assert resp.data['results'][0]['title'] == 'Docker Compose 実践入門'

    def test_no_match(self, api_client):
        _make_note('Docker', '# 本文')
        url = reverse('note-list') + '?search_title=Kubernetes'
        resp = api_client.get(url)
        assert resp.data['count'] == 0

    def test_fts5_case_insensitive(self, api_client):
        _make_note('DOCKER COMPOSE', '# 本文')
        url = reverse('note-list') + '?search_title=docker'
        resp = api_client.get(url)
        assert resp.data['count'] == 1


# ═══════════════════════════════════════════════════════════════════
# 複合 — title + content AND
# ═══════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestCombinedTitleContent:
    """?search_title= + ?search_content= の AND 検索。"""

    def test_both_match(self, api_client):
        _make_note('Docker入門', 'docker compose の基本。')
        _make_note('Docker中級', 'ネットワークの話。')
        url = reverse('note-list') + '?search_title=Docker&search_content=compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        assert resp.data['results'][0]['title'] == 'Docker入門'

    def test_title_match_content_not(self, api_client):
        _make_note('Docker入門', 'ネットワークの話。')
        url = reverse('note-list') + '?search_title=Docker&search_content=存在しない'
        resp = api_client.get(url)
        assert resp.data['count'] == 0

    def test_content_match_title_not(self, api_client):
        _make_note('Kubernetes入門', 'docker compose の話。')
        url = reverse('note-list') + '?search_title=Docker&search_content=compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 0


# ═══════════════════════════════════════════════════════════════════
# スニペット — _snippet field
# ═══════════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestSnippets:
    """リストAPI の _snippet フィールド検証。"""

    # ── REGEXP スニペット ──

    def test_regexp_snippet_contains_mark(self, api_client):
        """search_content → ヒット語が <mark> で包まれる"""
        _make_note('テスト', 'docker compose up でコンテナ起動。'
                  'ネットワーク設定は後述。' * 3)
        url = reverse('note-list') + '?search_content=compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        snip = resp.data['results'][0]['_snippet']
        assert snip is not None
        assert '<mark>compose</mark>' in snip

    def test_regexp_snippet_multiple_terms_highlighted(self, api_client):
        """AND 検索 → 全 term がハイライト"""
        _make_note('テスト', 'docker compose up で起動。' * 3)
        url = reverse('note-list') + '?search_content=docker compose'
        resp = api_client.get(url)
        snip = resp.data['results'][0]['_snippet']
        assert '<mark>docker</mark>' in snip
        assert '<mark>compose</mark>' in snip

    def test_regexp_snippet_window_truncation(self, api_client):
        """長文 → 前後が … で省略"""
        prefix = '前文。' * 30
        keyword = 'docker compose up'
        suffix = '後文。' * 30
        _make_note('テスト', f'{prefix}{keyword}{suffix}')
        url = reverse('note-list') + '?search_content=compose'
        resp = api_client.get(url)
        snip = resp.data['results'][0]['_snippet']
        assert snip.startswith('…')
        assert snip.endswith('…')
        assert '<mark>compose</mark>' in snip

    def test_regexp_snippet_no_match_none(self, api_client):
        """ヒットなし → _snippet は None"""
        _make_note('テスト', '無関係の文章。')
        url = reverse('note-list') + '?search_content=存在しない'
        resp = api_client.get(url)
        assert resp.data['count'] == 0

    def test_regexp_snippet_without_search_param_is_none(self, api_client):
        """検索パラメータなし → _snippet は None"""
        _make_note('テスト', '何かの文章。')
        url = reverse('note-list')
        resp = api_client.get(url)
        assert resp.data['results'][0]['_snippet'] is None

    # ── FTS5 スニペット ──

    def test_fts5_snippet_contains_mark(self, api_client):
        """search_title → FTS5 snippet() が <mark> で包む"""
        _make_note('Docker Compose 完全攻略', '# 本文')
        url = reverse('note-list') + '?search_title=Compose'
        resp = api_client.get(url)
        assert resp.data['count'] == 1
        snip = resp.data['results'][0]['_snippet']
        assert snip is not None
        assert '<mark>Compose</mark>' in snip

    # ── スニペット優先順位: content regex > title FTS5 ──

    def test_content_snippet_takes_priority_over_title(self, api_client):
        """title+content 両方指定時は content（REGEXP）スニペットが優先"""
        _make_note('Docker Compose 入門', 'kubernetes pod の管理方法。')
        url = reverse('note-list') + '?search_title=Docker&search_content=kubernetes'
        resp = api_client.get(url)
        snip = resp.data['results'][0]['_snippet']
        # content の REGEXP スニペットが使われる（kubernetes が Mark）
        assert '<mark>kubernetes</mark>' in snip
