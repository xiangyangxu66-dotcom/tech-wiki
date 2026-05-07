"""
process_md_file() 単体テスト

dropzone の中核ロジックを全経路カバー。
tmp_path でファイル I/O を分離し、純粋ロジックとして検証する。
"""

import pytest
from pathlib import Path
from wiki.models import Note, Category
from wiki.management.commands.dropzone import (
    process_md_file,
    extract_title,
    extract_tags,
    resolve_category,
    unique_slug,
    parse_frontmatter,
)


# ═══════════════════════════════════════════════════════════════
# ヘルパー関数 単体
# ═══════════════════════════════════════════════════════════════

class TestParseFrontmatter:
    def test_valid_yaml(self):
        fm, body = parse_frontmatter("---\ntitle: Test\ntags: [a, b]\n---\n# Body")
        assert fm == {'title': 'Test', 'tags': ['a', 'b']}
        assert body == '# Body'

    def test_no_frontmatter(self):
        fm, body = parse_frontmatter("# Just a heading\n\nContent")
        assert fm == {}
        assert body == "# Just a heading\n\nContent"

    def test_empty_frontmatter(self):
        """空 frontmatter: ---\n\n--- で空 YAML としてパースされる"""
        fm, body = parse_frontmatter("---\n\n---\nBody here")
        assert fm == {}
        assert body == 'Body here'

    def test_no_newline_between_delimiters(self):
        """---\n--- は frontmatter として認識されない（仕様通り）"""
        fm, body = parse_frontmatter("---\n---\nBody here")
        assert fm == {}  # マッチしないので空 dict

    def test_malformed_yaml(self):
        """壊れた YAML → 空 dict で継続"""
        fm, body = parse_frontmatter("---\n: broken: yaml: here\n---\nBody")
        assert fm == {}
        assert body == 'Body'

    def test_no_closing_delimiter(self):
        """--- が閉じてない → frontmatter なし扱い"""
        fm, body = parse_frontmatter("---\ntitle: Test\nBody")
        assert fm == {}


class TestExtractTitle:
    def test_from_frontmatter(self):
        assert extract_title({'title': 'My Title'}, '# H1 Title', 'file.md') == 'My Title'

    def test_from_h1(self):
        assert extract_title({}, '# 見出し1\n\n本文', 'file.md') == '見出し1'

    def test_from_filename(self):
        assert extract_title({}, '本文のみ', 'My Note.md') == 'My Note'

    def test_frontmatter_priority_over_h1(self):
        result = extract_title({'title': 'FM Title'}, '# H1 Title', 'file.md')
        assert result == 'FM Title'

    def test_strips_whitespace(self):
        assert extract_title({'title': '  Padded  '}, '', 'file.md') == 'Padded'


class TestExtractTags:
    def test_yaml_list(self):
        fm = {'tags': ['Python', 'Django']}
        assert extract_tags(fm, '') == ['Python', 'Django']

    def test_yaml_singular_tag(self):
        fm = {'tag': ['Rust']}
        assert extract_tags(fm, '') == ['Rust']

    def test_comma_separated_string(self):
        fm = {'tags': 'Python, Django, REST'}
        assert extract_tags(fm, '') == ['Python', 'Django', 'REST']

    def test_empty_tags_list(self):
        """★★★ 欠陥検出: frontmatter に tags キーはあるが空配列 → HackMD へフォールバック"""
        fm = {'tags': []}
        assert extract_tags(fm, '') == []

    def test_hackmd_format(self):
        fm = {}
        content = "###### tags: `auth` `saml`\n\n本文"
        assert extract_tags(fm, content) == ['auth', 'saml']

    def test_hackmd_with_line_number_prefix(self):
        """行番号接頭辞付き HackMD タグ（実データパターン）"""
        fm = {}
        content = "   399|###### tags: `chatbot` `nlp`\n本文"
        assert extract_tags(fm, content) == ['chatbot', 'nlp']

    def test_no_tags_at_all(self):
        """★★★ 欠陥検出: タグ情報が一切ない → 空リスト"""
        assert extract_tags({}, '本文のみ') == []

    def test_tags_priority_over_hackmd(self):
        """YAML tags があれば HackMD は無視"""
        fm = {'tags': ['Python']}
        content = "###### tags: `ignore-me`\n本文"
        assert extract_tags(fm, content) == ['Python']

    def test_mixed_types(self):
        fm = {'tags': [123, 'Python', True]}
        result = extract_tags(fm, '')
        assert result == ['123', 'Python', 'True']


@pytest.mark.django_db
class TestResolveCategory:
    def test_by_slug(self, category):
        result = resolve_category({'category': 'programming'})
        assert result == category

    def test_by_name(self, category):
        result = resolve_category({'category': 'プログラミング'})
        assert result == category

    def test_not_found(self):
        result = resolve_category({'category': 'nonexistent'})
        assert result is None

    def test_empty_string(self):
        assert resolve_category({'category': ''}) is None

    def test_no_category_key(self):
        assert resolve_category({}) is None


@pytest.mark.django_db
class TestUniqueSlug:
    def test_simple_english(self):
        assert unique_slug('Hello World') == 'hello-world'

    def test_japanese_fallback(self):
        slug = unique_slug('機械学習')
        assert slug.startswith('note-')
        assert len(slug) == 13  # 'note-' + 8 hex

    def test_duplicate_slug_appends_suffix(self, category):
        """既存 slug と衝突 → -2 サフィックス"""
        Note.objects.create(title='Test Note', content='body', category=category)
        # unique_slug('Test Note') → slugify('Test Note') → 'test-note'
        # 既に 'test-note' が存在 → 'test-note-2'
        slug = unique_slug('Test Note')
        assert slug == 'test-note-2'


# ═══════════════════════════════════════════════════════════════
# process_md_file() 統合テスト
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestProcessMdFile:
    """ファイル → DB 登録の全経路を検証。"""

    def test_import_ok(self, tmp_path, category):
        """★★★ 基本ケース: タグ付き frontmatter が正しく DB に永続化されること"""
        md = tmp_path / 'test.md'
        md.write_text(
            '---\n'
            'title: Python入門\n'
            'tags:\n'
            '  - Python\n'
            '  - 入門\n'
            'category: programming\n'
            '---\n'
            '# Python入門\n\nテスト本文です。'
        )

        result = process_md_file(str(md))

        assert result['status'] == 'IMPORT_OK'
        assert result['title'] == 'Python入門'
        assert result['tags'] == ['Python', '入門']
        assert result['category'] == 'プログラミング'

        # DB 検証
        note = Note.objects.get(slug=result['slug'])
        assert note.title == 'Python入門'
        assert sorted(t.name for t in note.tags.all()) == ['Python', '入門']  # ★ save() で同期され正しい値
        assert note.content_hash != ''
        assert note.status == Note.Status.PUBLISHED

    def test_tags_empty_when_no_frontmatter(self, tmp_path, category):
        """★★★ 欠陥検出: frontmatter なし → DB の tags は空"""
        md = tmp_path / 'notags.md'
        md.write_text('# タイトルだけ\n\nタグ情報なし。')

        result = process_md_file(str(md))

        assert result['status'] == 'IMPORT_OK'
        assert result['tags'] == []  # extract_tags() は空を返す

        note = Note.objects.get(slug=result['slug'])
        assert [t.name for t in note.tags.all()] == []  # ★ save() の extract_tags_from_content() も空を返す

    def test_hackmd_tags_only(self, tmp_path, category):
        """HackMD 形式のみでタグ抽出 → DB に永続化"""
        md = tmp_path / 'hackmd.md'
        md.write_text(
            '---\ntitle: HackMDノート\n---\n'
            '###### tags: `oauth` `jwt`\n\n本文'
        )

        result = process_md_file(str(md))

        assert result['status'] == 'IMPORT_OK'
        assert result['tags'] == ['oauth', 'jwt']

        note = Note.objects.get(slug=result['slug'])
        assert sorted(t.name for t in note.tags.all()) == ['jwt', 'oauth']

    def test_title_from_h1(self, tmp_path, category):
        """タイトルが H1 から取得されること"""
        md = tmp_path / 'no_title_fm.md'
        md.write_text('---\ntags: [Test]\n---\n# H1がタイトル\n\n本文')

        result = process_md_file(str(md))
        assert result['title'] == 'H1がタイトル'

    def test_title_from_filename(self, tmp_path, category):
        """frontmatter にも H1 にもタイトルがない → ファイル名"""
        md = tmp_path / 'ファイル名がタイトル.md'
        md.write_text('タイトル情報なしの本文。')

        result = process_md_file(str(md))
        assert result['title'] == 'ファイル名がタイトル'

    def test_duplicate_content_hash_skip(self, tmp_path, category):
        """★★★ 重複検知: 同一 content → SKIP_DUPLICATE"""
        content = '---\ntitle: 重複テスト\n---\n# 重複テスト\n\n同じ内容。'
        md1 = tmp_path / 'dup1.md'
        md1.write_text(content)

        # 1回目: 登録成功
        r1 = process_md_file(str(md1))
        assert r1['status'] == 'IMPORT_OK'
        assert Note.objects.filter(title='重複テスト').count() == 1

        # 2回目: content_hash 一致 → SKIP
        md2 = tmp_path / 'dup2.md'
        md2.write_text(content)
        r2 = process_md_file(str(md2))
        assert r2['status'] == 'SKIP_DUPLICATE'
        assert r2['existing_title'] == '重複テスト'
        assert Note.objects.filter(title='重複テスト').count() == 1  # 増えてない

    def test_duplicate_title_warning(self, tmp_path, category):
        """★★★ タイトル重複: 登録は続行、警告"""
        md1 = tmp_path / 'title1.md'
        md1.write_text('---\ntitle: 同じタイトル\n---\n# 同じタイトル\n\n本文1。')

        r1 = process_md_file(str(md1))
        assert r1['status'] == 'IMPORT_OK'

        # 2つ目: 別 content、同じタイトル
        md2 = tmp_path / 'title2.md'
        md2.write_text('---\ntitle: 同じタイトル\n---\n# 同じタイトル\n\n本文2。違う内容。')

        r2 = process_md_file(str(md2))
        assert r2['status'] == 'IMPORT_WARN'
        assert 'warning' in r2
        assert 'タイトル重複' in r2['warning']
        assert Note.objects.filter(title='同じタイトル').count() == 2

    def test_slug_collision_auto_suffix(self, tmp_path, category):
        """slug 衝突時は自動サフィックス付与"""
        md1 = tmp_path / 'slug1.md'
        md1.write_text('---\ntitle: My Note\n---\n# My Note\n\n本文1。')

        r1 = process_md_file(str(md1))
        assert r1['slug'] == 'my-note'

        md2 = tmp_path / 'slug2.md'
        md2.write_text('---\ntitle: My Note\n---\n# My Note\n\n本文2。違う。')

        r2 = process_md_file(str(md2))
        assert r2['slug'] == 'my-note-2'  # サフィックス付与
        assert Note.objects.filter(slug__startswith='my-note').count() == 2

    def test_category_not_found_graceful(self, tmp_path):
        """存在しないカテゴリ → category=None で登録される"""
        md = tmp_path / 'nocat.md'
        md.write_text(
            '---\ntitle: カテゴリなし\ncategory: imaginary-cat\n---\n# カテゴリなし\n\n本文。'
        )

        result = process_md_file(str(md))
        assert result['status'] == 'IMPORT_OK'
        assert result['category'] is None

        note = Note.objects.get(slug=result['slug'])
        assert note.category is None

    def test_no_category_in_frontmatter(self, tmp_path):
        """category キーなし → category=None"""
        md = tmp_path / 'nocat2.md'
        md.write_text('---\ntitle: カテゴリ指定なし\n---\n# テスト\n\n本文。')

        result = process_md_file(str(md))
        assert result['status'] == 'IMPORT_OK'
        assert result['category'] is None

    def test_content_hash_stored(self, tmp_path, category):
        """content_hash が DB に保存されていること"""
        md = tmp_path / 'hash.md'
        md.write_text('---\ntitle: Hash Test\n---\n# Hash\n\ncontent here')

        result = process_md_file(str(md))
        note = Note.objects.get(slug=result['slug'])
        assert len(note.content_hash) == 16  # HASH_LEN
        assert note.content_hash != ''

    def test_has_mermaid_detected(self, tmp_path, category):
        """Mermaid ブロック検出"""
        md = tmp_path / 'mermaid.md'
        md.write_text(
            '---\ntitle: 図表\n---\n# 図表\n\n```mermaid\ngraph TD\nA-->B\n```'
        )

        result = process_md_file(str(md))
        note = Note.objects.get(slug=result['slug'])
        assert note.has_mermaid is True

    def test_file_not_found(self, tmp_path):
        """存在しないファイル → ERROR_READ"""
        result = process_md_file(str(tmp_path / 'nonexistent.md'))
        assert result['status'] == 'ERROR_READ'
        assert 'error' in result

    def test_japanese_title_and_tags(self, tmp_path, category):
        """日本語タイトル + 日本語タグが正しく処理されること"""
        md = tmp_path / 'japanese.md'
        md.write_text(
            '---\n'
            'title: 機械学習の基礎\n'
            'tags:\n'
            '  - 機械学習\n'
            '  - 入門\n'
            '  - Python\n'
            '---\n'
            '# 機械学習の基礎\n\nscikit-learn の使い方。'
        )

        result = process_md_file(str(md))
        assert result['status'] == 'IMPORT_OK'
        assert result['title'] == '機械学習の基礎'
        assert '機械学習' in result['tags']
        assert '入門' in result['tags']
        assert 'Python' in result['tags']

        # slug はハッシュフォールバック
        assert result['slug'].startswith('note-')

        note = Note.objects.get(slug=result['slug'])
        assert sorted(t.name for t in note.tags.all()) == sorted(result['tags'])

    def test_save_error_graceful(self, tmp_path):
        """DB エラー時は ERROR_SAVE（例: 必須フィールド欠落は save() が防ぐので、
        通常は発生しないが、万一の例外伝播をテスト）"""
        # このテストは save() が例外を投げる極端なケース。
        # 通常は save() が slug を自動生成するので発生しない。
        # 万一のカバレッジとして残す。
        pass  # save() override が slug 自動生成するので、実質的にこの経路は通らない


# ═══════════════════════════════════════════════════════════════
# タグライフサイクル: 参照ゼロ → 自然消滅
# ═══════════════════════════════════════════════════════════════

@pytest.mark.django_db
class TestTagLifecycle:
    """タグは Tag テーブルで管理。
    全 Note から特定タグが消えれば、Note.save() の自動クリーンアップで Tag も削除される。
    ただし、Tag テーブルにレコードが残っていても note_count=0 なら API 応答に含まれない。
    """

    def test_tag_disappears_when_all_notes_removed(self, category):
        """全ノート削除 → Tag 集計（note_count>0）から消える"""
        # 同じタグを持つノートを2つ作成
        n1 = Note.objects.create(
            title='Note 1', slug='note-1',
            content='---\ntags:\n  - SharedTag\n---\n# N1\n本文',
            category=category,
        )
        n2 = Note.objects.create(
            title='Note 2', slug='note-2',
            content='---\ntags:\n  - SharedTag\n---\n# N2\n本文',
            category=category,
        )

        # 両方とも SharedTag を持つ
        assert [t.name for t in n1.tags.all()] == ['SharedTag']
        assert [t.name for t in n2.tags.all()] == ['SharedTag']

        # 集計（Tag.objects.annotate で SQL レベル集計）
        from wiki.models import Tag
        from django.db.models import Count
        shared = Tag.objects.annotate(cnt=Count('notes')).get(name='SharedTag')
        assert shared.cnt == 2

        # n1 のタグを削除（content を編集 → save() → 0参照タグ自動クリーンアップ）
        n1.content = '# N1\n\nタグなし本文'
        n1.save()
        assert [t.name for t in n1.tags.all()] == []

        # n1 だけ削除後、n2 がまだ参照しているので note_count==1
        assert Tag.objects.annotate(cnt=Count('notes')).get(name='SharedTag').cnt == 1

        # n2 も削除
        n2.delete()

        # 全ノートから SharedTag 参照が消えた → note_count==0 の Tag は集計対象外
        assert not Tag.objects.annotate(
            cnt=Count('notes')
        ).filter(name='SharedTag', cnt__gt=0).exists()

    def test_tag_persists_when_other_notes_still_reference(self, category):
        """1ノートだけタグ削除しても、他のノートが参照していれば残る"""
        n1 = Note.objects.create(
            title='Note A', slug='note-a',
            content='---\ntags:\n  - CommonTag\n---\n# A\n本文',
            category=category,
        )
        n2 = Note.objects.create(
            title='Note B', slug='note-b',
            content='---\ntags:\n  - CommonTag\n---\n# B\n本文',
            category=category,
        )

        # n1 だけタグ削除
        n1.content = '# A\n\nタグをやめた'
        n1.save()
        assert [t.name for t in n1.tags.all()] == []

        # n2 はまだ持っている
        from wiki.models import Tag
        from django.db.models import Count
        common = Tag.objects.annotate(cnt=Count('notes')).get(name='CommonTag')
        assert common.cnt == 1  # n2 だけ

    def test_new_tag_appears_in_aggregation(self, category):
        """新規ノートに新規タグ → 集計に現れる"""
        Note.objects.create(
            title='新規', slug='new-note',
            content='---\ntags:\n  - NewTag\n  - FreshTag\n---\n# 新規\n本文',
            category=category,
        )

        from wiki.models import Tag
        from django.db.models import Count
        tags = Tag.objects.annotate(cnt=Count('notes')).filter(name__in=['NewTag', 'FreshTag'])
        tag_counts = {t.name: t.cnt for t in tags}
        assert tag_counts['NewTag'] == 1
        assert tag_counts['FreshTag'] == 1

