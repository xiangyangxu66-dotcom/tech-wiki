import pytest
from django.urls import reverse
from wiki.models import Note, Category


# ── Category API ──────────────────────────────────────────────

@pytest.mark.django_db
def test_category_list_empty(api_client):
    url = reverse('category-list')
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] == 0


@pytest.mark.django_db
def test_category_list(tree, api_client):
    """ツリー: root ノードだけ返る (get_queryset が parent__isnull=True に制限)"""
    url = reverse('category-list')
    resp = api_client.get(url)
    assert resp.status_code == 200
    # tree fixture: '技術' だけが root
    assert resp.data['count'] == 1
    root_data = resp.data['results'][0]
    assert root_data['name'] == '技術'
    assert 'children' in root_data
    assert len(root_data['children']) == 2  # 言語, インフラ


@pytest.mark.django_db
def test_category_detail(tree, api_client):
    url = reverse('category-detail', kwargs={'pk': tree.pk})
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['name'] == '技術'


@pytest.mark.django_db
def test_category_404(api_client):
    url = reverse('category-detail', kwargs={'pk': 99999})
    resp = api_client.get(url)
    assert resp.status_code == 404


# ── Note API ───────────────────────────────────────────────────

@pytest.mark.django_db
def test_note_list_empty(api_client):
    url = reverse('note-list')
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] == 0


@pytest.mark.django_db
def test_note_list(note, api_client):
    url = reverse('note-list')
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] == 1
    n = resp.data['results'][0]
    assert n['title'] == 'Python入門'
    assert n['category_name'] == 'プログラミング'
    assert [t['name'] for t in n['tags']] == ['Python']


@pytest.mark.django_db
def test_note_list_multi(notes, api_client):
    url = reverse('note-list')
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] == 4


@pytest.mark.django_db
def test_note_detail(note, api_client):
    url = reverse('note-detail', kwargs={'slug': 'python-intro'})
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['title'] == 'Python入門'
    assert resp.data['content'].endswith('これはテストノートです。')
    assert [t['name'] for t in resp.data['tags']] == ['Python']
    assert resp.data['category_name'] == 'プログラミング'
    assert resp.data['category_slug'] == 'programming'


@pytest.mark.django_db
def test_note_detail_404(api_client):
    url = reverse('note-detail', kwargs={'slug': 'nonexistent'})
    resp = api_client.get(url)
    assert resp.status_code == 404


@pytest.mark.django_db
def test_note_create(api_client, category):
    url = reverse('note-list')
    payload = {
        'title': '新規ノート',
        'content': '---\ntags:\n  - NewTag\n---\n# 新規\n\nテスト',
        'category': category.id,
        'status': 'published',
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == 201
    assert resp.data['title'] == '新規ノート'
    assert resp.data['content'].endswith('テスト')
    assert resp.data['status'] == 'published'
    assert [t['name'] for t in resp.data['tags']] == ['NewTag']


@pytest.mark.django_db
def test_note_create_default_draft(api_client, category):
    """status 未指定時は draft になる"""
    url = reverse('note-list')
    payload = {
        'title': '下書きノート',
        'content': '# 下書き',
        'category': category.id,
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == 201
    assert resp.data['status'] == 'draft'


@pytest.mark.django_db
def test_note_create_bookmark(api_client, category):
    """ブックマーク付きノート作成"""
    url = reverse('note-list')
    payload = {
        'title': 'ブックマークノート',
        'content': '# 重要',
        'category': category.id,
        'bookmark': True,
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == 201
    assert resp.data['bookmark'] is True


@pytest.mark.django_db
def test_note_update(note, api_client):
    url = reverse('note-detail', kwargs={'slug': 'python-intro'})
    payload = {'title': 'Python超入門', 'content': '更新されました'}
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == 200
    assert resp.data['title'] == 'Python超入門'


@pytest.mark.django_db
def test_note_delete_not_allowed(note, api_client):
    """削除機能あり → 204 No Content"""
    url = reverse('note-detail', kwargs={'slug': 'python-intro'})
    resp = api_client.delete(url)
    assert resp.status_code == 204
    assert Note.objects.count() == 0


@pytest.mark.django_db
def test_note_create_invalid(api_client):
    """title なし → 400"""
    url = reverse('note-list')
    resp = api_client.post(url, {}, format='json')
    assert resp.status_code == 400
    body = resp.json()
    assert body['error']['code'] == 'E04001'


# ── Tag Aggregation API ───────────────────────────────────────

@pytest.mark.django_db
def test_tag_list(notes, api_client):
    url = reverse('tag-aggregation')
    resp = api_client.get(url)
    assert resp.status_code == 200
    names = {t['name'] for t in resp.data}
    assert 'Python' in names
    assert 'JavaScript' in names


@pytest.mark.django_db
def test_tag_note_count(notes, api_client):
    url = reverse('tag-aggregation')
    resp = api_client.get(url)
    results = resp.data
    python_tag = next(t for t in results if t['name'] == 'Python')
    assert python_tag['count'] == 2  # Python入門 + Pythonチートシート


# ── フィルタリング ─────────────────────────────────────────────

@pytest.mark.django_db
def test_note_filter_by_category(notes, api_client):
    url = reverse('note-list') + '?category__slug=programming'
    resp = api_client.get(url)
    assert resp.data['count'] == 2  # Python入門, Pythonチートシート
    titles = {n['title'] for n in resp.data['results']}
    assert 'Python入門' in titles
    assert 'Pythonチートシート' in titles


@pytest.mark.django_db
def test_note_filter_by_status(notes, api_client):
    url = reverse('note-list') + '?status=published'
    resp = api_client.get(url)
    assert resp.data['count'] == 4


@pytest.mark.django_db
def test_note_filter_by_bookmark(notes, api_client):
    """bookmark=True のノートだけ。Python入門のみ"""
    url = reverse('note-list') + '?bookmark=1'
    resp = api_client.get(url)
    assert resp.data['count'] == 1
    assert resp.data['results'][0]['title'] == 'Python入門'


@pytest.mark.django_db
def test_note_filter_by_tag(notes, api_client):
    url = reverse('note-list') + '?tag=python'
    resp = api_client.get(url)
    assert resp.data['count'] == 2  # Python入門, Pythonチートシート
    for n in resp.data['results']:
        assert 'Python' in n['title']


@pytest.mark.django_db
def test_note_filter_empty_result(notes, api_client):
    url = reverse('note-list') + '?tag=rust'
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] == 0


# ── 検索 ───────────────────────────────────────────────────────

@pytest.mark.django_db
def test_note_search_by_title(notes, api_client):
    url = reverse('note-list') + '?search=Python'
    resp = api_client.get(url)
    assert resp.data['count'] >= 2  # Python入門 + Pythonチートシート


@pytest.mark.django_db
def test_note_search_by_content(notes, api_client):
    """content フィールドに 'テストコンテンツ' が全ノートに入っている"""
    url = reverse('note-list') + '?search=テストコンテンツ'
    resp = api_client.get(url)
    assert resp.data['count'] == 4


# ── ページネーション ───────────────────────────────────────────

@pytest.mark.django_db
def test_note_pagination(api_client):
    """デフォルト page_size=20 で全ノートが1ページに収まることを確認"""
    Note.objects.all().delete()
    cat = Category.objects.create(name='テスト', slug='test-cat')
    for i in range(25):
        Note.objects.create(
            title=f'ノート{i:03d}',
            slug=f'note-{i:03d}',
            content=f'本文{i}',
            category=cat,
        )
    url = reverse('note-list')
    resp = api_client.get(url)
    assert resp.data['count'] == 25
    assert len(resp.data['results']) == 20  # 1ページ目 20件
    assert resp.data['next'] is not None

    # 2ページ目
    resp2 = api_client.get(resp.data['next'])
    assert resp2.status_code == 200
    assert len(resp2.data['results']) == 5
    assert resp2.data['next'] is None


# ── ソート ─────────────────────────────────────────────────────

@pytest.mark.django_db
def test_note_ordering_default(notes, api_client):
    """デフォルトは -bookmark → -updated_at（ブックマークが先頭、その中で更新順）"""
    url = reverse('note-list')
    resp = api_client.get(url)
    titles = [n['title'] for n in resp.data['results']]
    # Python入門 (bookmark=True) → JSチートシート → JS入門 → Pythonチートシート
    assert titles[0] == 'Python入門'  # bookmark が先頭


@pytest.mark.django_db
def test_note_ordering_by_title(notes, api_client):
    url = reverse('note-list') + '?ordering=title'
    resp = api_client.get(url)
    titles = [n['title'] for n in resp.data['results']]
    assert titles == sorted(titles)


# ── カテゴリ検索 ───────────────────────────────────────────────

@pytest.mark.django_db
def test_category_search(api_client):
    Category.objects.create(name='Python入門', slug='python-search')
    Category.objects.create(name='JavaScript中級', slug='js-search')
    url = reverse('category-list') + '?search=Python'
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data['count'] >= 1
