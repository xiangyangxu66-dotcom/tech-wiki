"""
dropzone: MD ファイル監視 & 自動登録 Django management command.

使い方:
    python manage.py dropzone [--dir <監視ディレクトリ>]

    起動後、監視ディレクトリに .md ファイルを放り込むと:
    1. ファイル読み取り → フロントマター解析（title, tags, category）
    2. 内容ハッシュで重複チェック（完全一致 → duplicates/ に移動）
    3. タイトル重複チェック（警告ログのみ、登録は続行）
    4. slug 重複時は自動サフィックス付与
    5. 登録成功 → processed/ に移動
    6. エラー時 → errors/ に移動（ログ出力）

重複判定ルール:
    - content_hash 一致 → SKIP（完全重複）
    - title 一致       → IMPORT_WARN（タイトル重複だがインポート続行）
    - slug 衝突        → AUTO_SLUG（-2, -3 サフィックス付与）

フロントマター書式:
    ---
    title: ノートのタイトル
    tags: [tag1, tag2]
    category: infra/docker
    ---
    # 本文がここから始まる
"""
import hashlib
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from wiki.models import HASH_LEN, Note, Category

logger = logging.getLogger('techwiki.dropzone')

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
H1_RE = re.compile(r'^#\s+(.+)$', re.MULTILINE)
HACKMD_TAGS_RE = re.compile(
    r'^\s*(?:\d+\|\s*)*#{1,6}\s*tags:\s*(`.+?`[\s,]*)+$', re.MULTILINE | re.IGNORECASE
)

# ---------------------------------------------------------------------------
# ヘルパー
# ---------------------------------------------------------------------------
def parse_frontmatter(text: str):
    """YAML frontmatter をパース。見つからなければ空 dict。"""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, text[m.end():]


def extract_title(fm: dict, body: str, filename: str) -> str:
    """タイトル解決: frontmatter.title → 本文の最初の H1 → ファイル名（拡張子除く）"""
    if fm.get('title'):
        return str(fm['title']).strip()
    m = H1_RE.search(body)
    if m:
        return m.group(1).strip()
    return Path(filename).stem


def extract_tags(fm: dict, full_content: str = '') -> list:
    """タグを文字列リストに正規化。
    1. YAML frontmatter tags/tag
    2. HackMD 形式 `###### tags: `tag1` `tag2``
    """
    raw = fm.get('tags', [])
    if not raw:
        raw = fm.get('tag', [])
    if raw:
        if isinstance(raw, str):
            raw = [t.strip() for t in raw.split(',')]
        tags = [str(t).strip() for t in raw if str(t).strip()]
        if tags:
            return tags
    # HackMD 形式
    m = HACKMD_TAGS_RE.search(full_content)
    if m:
        return [t.strip() for t in re.findall(r'`([^`]+)`', m.group(0)) if t.strip()]
    return []


def resolve_category(fm: dict):
    """カテゴリ解決: frontmatter.category (slug or name) → Category or None"""
    raw = fm.get('category', '')
    if not raw:
        # tags[0] をカテゴリ候補にしない（安易な推測は誤登録の元）
        return None
    raw = str(raw).strip()
    for lookup in ['slug', 'name']:
        try:
            return Category.objects.get(**{lookup: raw})
        except Category.DoesNotExist:
            continue
    logger.warning(f'Category not found: {raw}')
    return None


def unique_slug(title: str) -> str:
    """slug 重複を避けてユニークな slug を生成（-2, -3, ... サフィックス）。"""
    base = slugify(title) or f'note-{hashlib.md5(title.encode()).hexdigest()[:8]}'
    slug = base
    counter = 2
    while Note.objects.filter(slug=slug).exists():
        slug = f'{base}-{counter}'
        counter += 1
    return slug


# ---------------------------------------------------------------------------
# ファイル処理
# ---------------------------------------------------------------------------
def process_md_file(filepath: str) -> dict:
    """1ファイルを処理し、結果を辞書で返す。"""
    filepath = Path(filepath)
    filename = filepath.name

    # 読み取り
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        return {'status': 'ERROR_READ', 'filename': filename, 'error': str(e)}

    fm, body = parse_frontmatter(content)
    title = extract_title(fm, body, filename)
    tags = extract_tags(fm, content)
    content_hash = hashlib.md5(content.encode()).hexdigest()[:HASH_LEN]

    # 重複チェック1: content_hash 完全一致
    if Note.objects.filter(content_hash=content_hash).exists():
        dup = Note.objects.filter(content_hash=content_hash).first()
        return {
            'status': 'SKIP_DUPLICATE',
            'filename': filename,
            'title': title,
            'existing_slug': dup.slug,
            'existing_title': dup.title,
        }

    # 重複チェック2: タイトル一致（警告のみ、登録は続行）
    title_dup = Note.objects.filter(title=title).exists()

    # カテゴリ解決
    category = resolve_category(fm)

    # slug 生成
    slug = unique_slug(title)

    # Note 作成
    try:
        note = Note.objects.create(
            title=title,
            slug=slug,
            content=content,
            note_tags=tags,
            category=category,
            status=Note.Status.PUBLISHED,
        )
    except Exception as e:
        return {'status': 'ERROR_SAVE', 'filename': filename, 'title': title, 'error': str(e)}

    result = {
        'status': 'IMPORT_WARN' if title_dup else 'IMPORT_OK',
        'filename': filename,
        'title': title,
        'slug': slug,
        'tags': tags,
        'category': category.name if category else None,
        'note_id': note.id,
    }
    if title_dup:
        result['warning'] = f'タイトル重複: "{title}" は既に存在します'
    return result


# ---------------------------------------------------------------------------
# watchdog ハンドラ
# ---------------------------------------------------------------------------
class DropzoneHandler(FileSystemEventHandler):
    def __init__(self, stdout, processed_dir, duplicates_dir, errors_dir):
        self.stdout = stdout
        self.processed_dir = Path(processed_dir)
        self.duplicates_dir = Path(duplicates_dir)
        self.errors_dir = Path(errors_dir)
        self._recent = set()  # 短時間での重複イベント防止

    def on_any_event(self, event):
        """macOS の cp/mv で created が発火しないケースに対応"""
        if event.is_directory:
            return
        src_path = event.src_path
        if not src_path.endswith('.md'):
            return

        src = Path(src_path)
        if not src.exists():
            return
        # 短時間重複イベント防止
        key = str(src.resolve())
        if key in self._recent:
            return
        self._recent.add(key)
        # 1秒後にクリア（別ファイルなら問題なし）
        time.sleep(0.5)
        if not src.exists():
            self._recent.discard(key)
            return

        self._process(src)
        self._recent.discard(key)

    def _process(self, src: Path):
        self.stdout.write(f'\n📥 検出: {src.name}')
        self.stdout.flush()

        result = process_md_file(str(src))

        self.stdout.write(f'   → {result["status"]}: {result.get("title", "?")}')
        self.stdout.flush()

        if result['status'] == 'SKIP_DUPLICATE':
            self.stdout.write(f'      ⚠ 重複: 既存 "{result["existing_title"]}" (slug={result["existing_slug"]})')
            self._move(src, self.duplicates_dir)

        elif result['status'].startswith('ERROR'):
            self.stdout.write(f'      ❌ {result.get("error", "")}')
            self._move(src, self.errors_dir)

        else:
            self.stdout.write(f'      ✅ slug={result["slug"]} tags={result.get("tags", [])} cat={result.get("category", "-")}')
            warning = result.get('warning')
            if warning:
                self.stdout.write(f'      ⚠ {warning}')
            self._move(src, self.processed_dir)
        self.stdout.flush()

    def _move(self, src, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        # 同名ファイル衝突時はタイムスタンプ付与
        if dest.exists():
            dest = dest_dir / f'{src.stem}_{int(time.time())}{src.suffix}'
        shutil.move(str(src), str(dest))


# ---------------------------------------------------------------------------
# コマンド
# ---------------------------------------------------------------------------
class Command(BaseCommand):
    help = 'MD ファイルを監視し、自動で Note として登録する（重複検知付き）'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dir', default=None,
            help='監視ディレクトリ（デフォルト: <project_root>/dropzone/）'
        )

    def handle(self, *args, **options):
        watch_dir = Path(options['dir']) if options['dir'] else settings.BASE_DIR.parent / 'dropzone'
        watch_dir.mkdir(parents=True, exist_ok=True)

        processed_dir = watch_dir / 'processed'
        duplicates_dir = watch_dir / 'duplicates'
        errors_dir = watch_dir / 'errors'

        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('  Tech-Wiki Dropzone'))
        self.stdout.write(self.style.SUCCESS(f'  監視ディレクトリ: {watch_dir}'))
        self.stdout.write(self.style.SUCCESS(f'  処理済:           {processed_dir}'))
        self.stdout.write(self.style.SUCCESS(f'  重複:             {duplicates_dir}'))
        self.stdout.write(self.style.SUCCESS(f'  エラー:           {errors_dir}'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('  .md ファイルをドロップすると自動登録されます')
        self.stdout.write('  Ctrl+C で停止\n')

        # ★ 起動時に既存の .md ファイルを一括処理
        existing = sorted(watch_dir.glob('*.md'))
        if existing:
            self.stdout.write(f'\n  起動時スキャン: {len(existing)} 件の未処理ファイル')
            self.stdout.flush()
            for f in existing:
                result = process_md_file(str(f))
                self.stdout.write(f'  📥 {f.name} → {result["status"]}: {result.get("title", "?")}')
                self.stdout.flush()
                if result['status'] == 'SKIP_DUPLICATE':
                    shutil.move(str(f), str(duplicates_dir / f.name))
                elif result['status'].startswith('ERROR'):
                    shutil.move(str(f), str(errors_dir / f.name))
                else:
                    shutil.move(str(f), str(processed_dir / f.name))
            self.stdout.write('  起動時スキャン完了\n')
            self.stdout.flush()

        event_handler = DropzoneHandler(
            stdout=self.stdout,
            processed_dir=processed_dir,
            duplicates_dir=duplicates_dir,
            errors_dir=errors_dir,
        )
        observer = Observer()
        observer.schedule(event_handler, str(watch_dir), recursive=False)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            self.stdout.write('\n🛑 監視を停止しました')
        observer.join()
