import pytest
from rest_framework.test import APIClient
from wiki.models import Category, Note

# Re-export factories so tests can do `from conftest import make_*`
from tests.factories import (   # noqa: F401 — imported for test convenience
    make_category, make_category_tree, make_category_flat,
    make_note, make_note_set, make_paginated_notes,
    make_full_scenario,
)


# ── Basic fixtures ──────────────────────────────────────────────

@pytest.fixture
def api_client():
    """DRF APIClient fixture."""
    return APIClient()


@pytest.fixture
def category(db):
    return Category.objects.create(name='プログラミング', slug='programming')


@pytest.fixture
def child_category(db, category):
    return Category.objects.create(name='Python', slug='python-cat', parent=category)


@pytest.fixture
def note(db, category):
    return Note.objects.create(
        title='Python入門',
        slug='python-intro',
        content='---\ntags:\n  - Python\n---\n# Python入門\n\nこれはテストノートです。',
        category=category,
        status=Note.Status.PUBLISHED,
    )


@pytest.fixture
def notes(db, category, child_category):
    """4ノート: Python入門, Pythonチートシート, JS入門, JSチートシート"""
    data = [
        ('Python入門', category, ['Python', '入門'], True),
        ('Pythonチートシート', category, ['Python', 'チートシート'], False),
        ('JavaScript入門', child_category, ['JavaScript', '入門'], False),
        ('JavaScriptチートシート', child_category, ['JavaScript', 'チートシート'], False),
    ]
    created = []
    for title, cat, tag_list, bookmark in data:
        tag_lines = '\n'.join(f'  - {tag}' for tag in tag_list)
        n = Note.objects.create(
            title=title,
            slug=title.lower().replace(' ', '-').replace('ー', '-'),
            content=f'---\ntags:\n{tag_lines}\n---\n# {title}\n\nテストコンテンツ。',
            category=cat,
            bookmark=bookmark,
            status=Note.Status.PUBLISHED,
        )
        created.append(n)
    return created


@pytest.fixture
def tree(db):
    """3階層のカテゴリツリー: 技術 > 言語 > Python/JS, インフラ > Docker"""
    root = Category.objects.create(name='技術', slug='tech')
    lang = Category.objects.create(name='言語', slug='lang', parent=root)
    Category.objects.create(name='Python', slug='python-child', parent=lang)
    Category.objects.create(name='JavaScript', slug='javascript-child', parent=lang)
    infra = Category.objects.create(name='インフラ', slug='infra', parent=root)
    Category.objects.create(name='Docker', slug='docker', parent=infra)
    Category.objects.rebuild()
    return Category.objects.get(slug='tech')


# ── 追加 fixtures ───────────────────────────────────────────────

@pytest.fixture
def empty_db(db):
    """空の DB（fixture 未使用時に明示的に使う）。"""
    return None


@pytest.fixture
def category_deep_tree(db):
    """5階層の深いカテゴリツリー。"""
    root = Category.objects.create(name='L0', slug='l0')
    parent = root
    for i in range(1, 5):
        parent = Category.objects.create(name=f'L{i}', slug=f'l{i}', parent=parent)
    Category.objects.rebuild()
    return Category.objects.get(slug='l0')


@pytest.fixture
def full_scenario(db):
    """統合シナリオ fixture。factories.make_full_scenario() のラッパー。"""
    return make_full_scenario()
