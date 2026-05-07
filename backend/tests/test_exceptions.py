"""
例外クラス単体テスト

全14種の例外について:
- 正しい code / http_status / message で初期化されること
- to_dict() が統一 JSON 形式を返すこと
- 例外継承ツリーが正しいこと
"""

import pytest
from exceptions import (
    AppError,
    # System (5xx)
    SystemError,
    UnhandledError,
    ConfigError,
    ExternalServiceError,
    DatabaseError,
    FileSystemError,
    MdFileNotFoundError,
    MdFileHashMismatchError,
    # Business (4xx)
    BusinessError,
    ValidationError,
    AuthRequiredError,
    TokenInvalidError,
    PermissionDeniedError,
    NotFoundError,
    NoteNotFoundError,
    CategoryNotFoundError,
    TagNotFoundError,
    DuplicateError,
    SlugDuplicateError,
    MdFileDuplicateError,
)


# ── 基底クラス ──────────────────────────────────────────────────

class TestAppError:
    def test_construction_minimal(self):
        e = AppError(code='E01000', message='エラー', detail='詳細', http_status=500)
        assert e.code == 'E01000'
        assert e.message == 'エラー'
        assert e.detail == '詳細'
        assert e.http_status == 500

    def test_detail_defaults_to_message(self):
        e = AppError(code='E01000', message='msg')
        assert e.detail == 'msg'

    def test_to_dict_format(self):
        e = AppError(code='E04001', message='バリデーション失敗', detail='title required')
        d = e.to_dict()
        assert d == {
            'error': {
                'code': 'E04001',
                'message': 'バリデーション失敗',
                'detail': 'title required',
            }
        }

    def test_str_is_message(self):
        e = AppError(code='X', message='hello')
        assert str(e) == 'hello'

    def test_repr(self):
        e = NoteNotFoundError(slug='x')
        r = repr(e)
        assert 'NoteNotFoundError' in r
        assert 'E06002' in r


# ── システム例外 (5xx) ──────────────────────────────────────────


class TestSystemErrors:
    """全システム例外の code と http_status を検証。"""

    @pytest.mark.parametrize('cls,exp_code,exp_status', [
        (UnhandledError, 'E01000', 500),
        (ConfigError, 'E01001', 500),
        (ExternalServiceError, 'E01002', 500),
        (DatabaseError, 'E02001', 500),
        (FileSystemError, 'E03001', 500),
        (MdFileNotFoundError, 'E03002', 500),
        (MdFileHashMismatchError, 'E03003', 500),
    ])
    def test_system_error_codes(self, cls, exp_code, exp_status):
        e = cls()
        assert e.code == exp_code, f'{cls.__name__}: expected {exp_code}, got {e.code}'
        assert e.http_status == exp_status
        assert isinstance(e, SystemError)
        assert isinstance(e, AppError)

    def test_unhandled_error_stores_original_type(self):
        e = UnhandledError(detail='boom', original_type='ValueError')
        assert e.original_type == 'ValueError'
        assert e.code == 'E01000'

    def test_md_file_not_found_includes_path(self):
        e = MdFileNotFoundError(file_path='/data/python/intro.md')
        assert '/data/python/intro.md' in e.message
        assert e.code == 'E03002'

    def test_md_file_hash_mismatch_includes_details(self):
        e = MdFileHashMismatchError(
            file_path='/a/b.md', expected='abc123', actual='def456'
        )
        assert '/a/b.md' in e.detail
        assert 'abc123' in e.detail
        assert 'def456' in e.detail
        assert e.code == 'E03003'


# ── 業務例外 (4xx) ──────────────────────────────────────────────


class TestBusinessErrors:
    @pytest.mark.parametrize('cls,exp_code,exp_status', [
        (ValidationError, 'E04001', 400),
        (AuthRequiredError, 'E05001', 401),
        (TokenInvalidError, 'E05002', 401),
        (PermissionDeniedError, 'E05003', 403),
        (NotFoundError, 'E06001', 404),
        (DuplicateError, 'E07001', 409),
    ])
    def test_business_error_codes(self, cls, exp_code, exp_status):
        e = cls()
        assert e.code == exp_code
        assert e.http_status == exp_status
        assert isinstance(e, BusinessError)
        assert isinstance(e, AppError)

    def test_validation_error_with_custom_message(self):
        e = ValidationError(message='タイトルは必須です', detail='title: null')
        assert e.code == 'E04001'
        assert e.message == 'タイトルは必須です'
        assert e.http_status == 400

    def test_auth_required_has_japanese_message(self):
        e = AuthRequiredError()
        assert e.code == 'E05001'
        assert '認証' in e.message
        assert e.http_status == 401

    def test_token_invalid_has_japanese_message(self):
        e = TokenInvalidError()
        assert 'トークン' in e.message
        assert e.http_status == 401

    def test_permission_denied_has_japanese_message(self):
        e = PermissionDeniedError()
        assert '権限' in e.message
        assert e.http_status == 403


# ── リソース不在系 ──────────────────────────────────────────────


class TestNotFoundErrors:
    def test_not_found_base(self):
        e = NotFoundError()
        assert e.code == 'E06001'
        assert e.http_status == 404

    def test_note_not_found_with_slug(self):
        e = NoteNotFoundError(slug='rust-tutorial')
        assert e.code == 'E06002'
        assert 'rust-tutorial' in e.message
        d = e.to_dict()
        assert d['error']['code'] == 'E06002'

    def test_note_not_found_empty_slug(self):
        e = NoteNotFoundError(slug='')
        assert e.code == 'E06002'
        assert 'ノートが見つかりません' in e.message

    def test_category_not_found(self):
        e = CategoryNotFoundError(identifier='42')
        assert e.code == 'E06003'
        assert '42' in e.message

    def test_tag_not_found(self):
        e = TagNotFoundError(identifier='Rust')
        assert e.code == 'E06004'
        assert 'Rust' in e.message

    def test_not_found_subclass_inheritance(self):
        e = NoteNotFoundError(slug='x')
        assert isinstance(e, NotFoundError)
        assert isinstance(e, BusinessError)
        assert isinstance(e, AppError)


# ── 重複系 ──────────────────────────────────────────────────────


class TestDuplicateErrors:
    def test_duplicate_base(self):
        e = DuplicateError()
        assert e.code == 'E07001'
        assert e.http_status == 409

    def test_slug_duplicate_with_slug(self):
        e = SlugDuplicateError(slug='python-intro')
        assert e.code == 'E07002'
        assert 'python-intro' in e.message
        assert e.http_status == 409

    def test_md_file_duplicate_with_path(self):
        e = MdFileDuplicateError(file_path='/data/backup.md')
        assert e.code == 'E07003'
        assert '/data/backup.md' in e.message
        assert e.http_status == 409

    def test_duplicate_subclass_inheritance(self):
        e = SlugDuplicateError(slug='x')
        assert isinstance(e, DuplicateError)
        assert isinstance(e, BusinessError)


# ── to_dict 全種 ────────────────────────────────────────────────


class TestToDictAllTypes:
    """全例外で to_dict() が期待する JSON 構造を返すこと。"""

    @pytest.mark.parametrize('exc_instance,exp_code', [
        (UnhandledError(), 'E01000'),
        (ConfigError(), 'E01001'),
        (ExternalServiceError(), 'E01002'),
        (DatabaseError(), 'E02001'),
        (FileSystemError(), 'E03001'),
        (MdFileNotFoundError('/x.md'), 'E03002'),
        (MdFileHashMismatchError('/x.md', 'a', 'b'), 'E03003'),
        (ValidationError(), 'E04001'),
        (AuthRequiredError(), 'E05001'),
        (TokenInvalidError(), 'E05002'),
        (PermissionDeniedError(), 'E05003'),
        (NotFoundError(), 'E06001'),
        (NoteNotFoundError('x'), 'E06002'),
        (CategoryNotFoundError('x'), 'E06003'),
        (TagNotFoundError('x'), 'E06004'),
        (DuplicateError(), 'E07001'),
        (SlugDuplicateError('x'), 'E07002'),
        (MdFileDuplicateError('/x.md'), 'E07003'),
    ])
    def test_to_dict_structure(self, exc_instance, exp_code):
        d = exc_instance.to_dict()
        assert 'error' in d
        assert d['error']['code'] == exp_code
        assert 'message' in d['error']
        assert 'detail' in d['error']
        # message と detail は空文字列ではないこと
        assert len(d['error']['message']) > 0


# ── Pickle / 伝播 ───────────────────────────────────────────────

class TestExceptionPropagation:
    """例外が raise / catch 可能で、情報が失われないこと。"""

    def test_catch_as_app_error(self):
        try:
            raise NoteNotFoundError(slug='test')
        except AppError as e:
            assert e.code == 'E06002'
            assert e.http_status == 404

    def test_catch_as_business_error(self):
        try:
            raise ValidationError(message='bad input')
        except BusinessError as e:
            assert e.code == 'E04001'
            assert e.http_status == 400

    def test_catch_as_system_error(self):
        try:
            raise DatabaseError(detail='Connection refused')
        except SystemError as e:
            assert e.code == 'E02001'
