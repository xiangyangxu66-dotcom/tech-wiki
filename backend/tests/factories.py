"""
テスト用データ生成ヘルパー (Factory helpers)

factory_boy が入っていない環境でも使えるよう、素の Django モデル呼び出しで構築。
各関数は生成したインスタンスを返す。複数まとめて使う場合は build_*_set() 系を使う。
"""

from wiki.models import Category, Note


# ── Category (MPTT) ─────────────────────────────────────────────

def make_category(name='テクノロジー', slug=None, parent=None) -> Category:
    """単一カテゴリ生成。"""
    c = Category.objects.create(name=name, slug=slug or '', parent=parent)
    return c


def make_category_tree(spec: list[tuple]) -> Category:
    """
    カテゴリツリーを一括構築。spec は (name, children) のタプルリスト。
    子がいない場合は (name, [])。

    例:
        root = make_category_tree([
            ('技術', [
                ('Python', []),
                ('JavaScript', []),
            ]),
            ('デザイン', []),
        ])
    """
    def _build(name, children, parent):
        cat = make_category(name, parent=parent)
        for child_name, child_children in children:
            _build(child_name, child_children, cat)
        return cat

    # ルートは親なしで作成
    root_name, root_children = spec[0]
    root = make_category(root_name)
    for child_name, child_children in root_children:
        _build(child_name, child_children, root)
    Category.objects.rebuild()  # MPTT 再構築
    return Category.objects.get(id=root.id)


def make_category_flat(count=5) -> list[Category]:
    """フラットなカテゴリを count 件生成。"""
    return [make_category(name=f'カテゴリ {i:02d}') for i in range(count)]


# ── Note ────────────────────────────────────────────────────────

def make_note(
    title='テストノート',
    slug=None,
    content='# テスト\n\nテストコンテンツ',
    category=None,
    bookmark=False,
    status=Note.Status.PUBLISHED,
) -> Note:
    """単一ノート生成。タグは content frontmatter から抽出される。"""
    return Note.objects.create(
        title=title,
        slug=slug or '',
        content=content,
        category=category,
        bookmark=bookmark,
        status=status,
    )


def make_note_set(
    specs: list[dict],
    default_category=None,
) -> list[Note]:
    """
    ノートを一括生成。各 spec は dict:
        {'title': '...', 'content': '...', 'category': ...}

    spec に含まれない項目は default_category が使われる。
    """
    created = []
    for spec in specs:
        n = Note.objects.create(
            title=spec.get('title', 'Untitled'),
            slug=spec.get('slug', ''),
            content=spec.get('content', '# Untitled'),
            category=spec.get('category', default_category),
            bookmark=spec.get('bookmark', False),
            status=spec.get('status', Note.Status.PUBLISHED),
        )
        created.append(n)
    return created


def make_paginated_notes(count=25, category=None) -> list[Note]:
    """ページネーションテスト用に count 件のノートを生成。"""
    return [
        Note.objects.create(
            title=f'ノート {i:03d}',
            slug=f'note-{i:03d}',
            content=f'本文 {i}',
            category=category,
        )
        for i in range(count)
    ]


# ── Combined ────────────────────────────────────────────────────

def make_full_scenario() -> dict:
    """
    統合シナリオ: カテゴリツリー + タグセット + ノートセット をまとめて返す。

    Returns:
        {'categories': Category(ルート), 'notes': list[Note]}
    """
    root = make_category_tree([
        ('技術', [
            ('バックエンド', [
                ('Python', []),
                ('Node.js', []),
            ]),
            ('フロントエンド', [
                ('React', []),
                ('Vue', []),
            ]),
            ('インフラ', [
                ('Docker', []),
                ('Kubernetes', []),
            ]),
        ]),
    ])
    # ルート直下のカテゴリを取得
    backend = root.get_children().get(name='バックエンド')
    python_cat = backend.get_children().get(name='Python')
    infra = root.get_children().get(name='インフラ')
    docker_cat = infra.get_children().get(name='Docker')

    notes = make_note_set([
        {
            'title': 'Python入門',
            'content': '---\ntags:\n  - Python\n  - 入門\n---\n# Python入門\n\nPythonの基礎を学ぶ。',
            'category': python_cat,
            'bookmark': True,
        },
        {
            'title': 'Pythonチートシート',
            'content': '---\ntags:\n  - Python\n  - チートシート\n---\n# Pythonチートシート\n\nよく使う構文まとめ。',
            'category': python_cat,
        },
        {
            'title': 'Docker入門',
            'content': '---\ntags:\n  - Docker\n  - 入門\n---\n# Docker入門\n\nコンテナの基礎。',
            'category': docker_cat,
        },
        {
            'title': 'Docker Compose',
            'content': '---\ntags:\n  - Docker\n---\n# Docker Compose\n\nマルチコンテナ管理。',
            'category': docker_cat,
        },
    ])
    return {'categories': root, 'notes': notes}
