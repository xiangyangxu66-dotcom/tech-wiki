import pytest
from wiki.models import Category, Note, _slugify_with_fallback


# ── _slugify_with_fallback 単体 ──────────────────────────────

def test_slugify_english():
    assert _slugify_with_fallback('Hello World') == 'hello-world'


def test_slugify_japanese():
    """日本語のみ → 空 slug → ハッシュにフォールバック"""
    result = _slugify_with_fallback('入門')
    assert result.startswith('')
    assert len(result) == 8  # MD5 hex 8 桁


def test_slugify_japanese_with_prefix():
    result = _slugify_with_fallback('入門', 'tag-')
    assert result.startswith('tag-')
    assert len(result) == 12  # 'tag-' + 8


def test_slugify_mixed():
    """英語+日本語 → 英語だけ slugify される"""
    result = _slugify_with_fallback('Python入門')
    assert 'python' in result


def test_slugify_empty_string():
    result = _slugify_with_fallback('', 'note-')
    assert result.startswith('note-')
    assert len(result) == 13  # 'note-' + 8


# ── Category モデル (MPTT) ────────────────────────────────────

@pytest.mark.django_db
def test_category_create_root():
    c = Category.objects.create(name='プログラミング', slug='prog')
    assert c.parent is None
    assert c.is_root_node() is True


@pytest.mark.django_db
def test_category_create_child():
    parent = Category.objects.create(name='技術', slug='tech')
    child = Category.objects.create(name='Python', slug='python', parent=parent)
    assert child.parent == parent
    assert child.is_child_node() is True
    assert parent.get_children().count() == 1


@pytest.mark.django_db
def test_category_tree_three_levels(tree):
    """conftest の tree fixture: 技術 > 言語 > Python"""
    root = tree
    assert root.get_descendant_count() == 5  # 全子孫
    children = root.get_children()
    assert children.count() == 2  # 言語, インフラ
    lang = children.get(name='言語')
    lang_children = lang.get_children()
    assert lang_children.count() == 2  # Python, JavaScript


@pytest.mark.django_db
def test_category_note_count(category, note):
    assert category.notes.count() == 1
    assert category.notes.first().title == 'Python入門'


# ── Note モデル ────────────────────────────────────────────────

@pytest.mark.django_db
def test_note_create(category):
    n = Note.objects.create(
        title='テスト', slug='test', content='---\ntags:\n  - Python\n---\n# Test',
        category=category, status=Note.Status.PUBLISHED,
    )
    assert n.title == 'テスト'
    assert n.category == category
    assert n.note_tags == ['Python']
    assert n.status == Note.Status.PUBLISHED


@pytest.mark.django_db
def test_note_default_status_draft(category):
    """status 未指定時は draft"""
    n = Note.objects.create(title='下書き', content='本文', category=category)
    assert n.status == Note.Status.DRAFT


@pytest.mark.django_db
def test_note_bookmark_default(category):
    """bookmark デフォルトは False"""
    n = Note.objects.create(title='普通', content='本文', category=category)
    assert n.bookmark is False


@pytest.mark.django_db
def test_note_slug_auto_generate_english(category):
    n = Note.objects.create(title='My Note', content='body', category=category)
    assert n.slug == 'my-note'


@pytest.mark.django_db
def test_note_slug_auto_generate_japanese(category):
    n = Note.objects.create(title='機械学習入門', content='本文', category=category)
    assert len(n.slug) > 0
    assert n.slug.startswith('note-')


@pytest.mark.django_db
def test_note_without_category():
    n = Note.objects.create(title='単独ノート', content='本文')
    assert n.category is None


@pytest.mark.django_db
def test_note_multiple_tags_from_frontmatter(category):
    n = Note.objects.create(
        title='ノート',
        content='---\ntags:\n  - Python\n  - 入門\n---\n本文',
        category=category,
    )
    assert n.note_tags == ['Python', '入門']


@pytest.mark.django_db
def test_note_hackmd_tags(category):
    n = Note.objects.create(
        title='HackMDタグ',
        content='###### tags: `auth` `saml`\n\n本文',
        category=category,
    )
    assert n.note_tags == ['auth', 'saml']


@pytest.mark.django_db
def test_note_has_mermaid(category):
    n = Note.objects.create(
        title='図表ノート',
        content='```mermaid\ngraph TD\nA-->B\n```',
        category=category,
    )
    assert n.has_mermaid is True


@pytest.mark.django_db
def test_note_without_mermaid(category):
    n = Note.objects.create(title='通常ノート', content='```python\nprint(1)\n```', category=category)
    assert n.has_mermaid is False


@pytest.mark.django_db
def test_note_str(note):
    assert str(note) == 'Python入門'


@pytest.mark.django_db
def test_note_ordering_bookmark_first(category):
    """bookmark=True が先頭、その中では updated_at 降順"""
    import time
    n1 = Note.objects.create(title='ブックマーク', content='bm', category=category, bookmark=True)
    time.sleep(1.1)
    n2 = Note.objects.create(title='通常', content='normal', category=category, bookmark=False)
    notes = list(Note.objects.all())
    assert notes[0].title == 'ブックマーク'
    assert notes[0].bookmark is True


@pytest.mark.django_db
def test_note_ordering_default(category):
    """updated_at 降順（bookmark がない場合）"""
    import time
    n1 = Note.objects.create(title='古い', content='old', category=category)
    time.sleep(1.1)
    n2 = Note.objects.create(title='新しい', content='new', category=category)
    notes = list(Note.objects.all())
    assert notes[0].title == '新しい'
