"""
エラーハンドラ結合テスト

config.error_handler.exception_handler() が
全例外パターンを正しく JSON 形式に変換することを検証する。

テスト対象:
1. 自前 AppError サブクラス → 自身の code/message/detail/http_status を使用
2. DRF ネイティブ例外 → 定義済みエラーコードにマッピング
3. Django DB 例外 → E02001 DatabaseError
4. その他 Python 例外 → E01000 UnhandledError
"""

import json
import pytest
from django.db import OperationalError

from rest_framework.exceptions import (
    NotFound as DRFNotFound,
    PermissionDenied as DRFPermissionDenied,
    AuthenticationFailed as DRFAuthenticationFailed,
    NotAuthenticated as DRFNotAuthenticated,
    ValidationError as DRFValidationError,
    ParseError as DRFParseError,
)

from config.error_handler import exception_handler
from exceptions import (
    NoteNotFoundError,
    CategoryNotFoundError,
    TagNotFoundError,
    ValidationError,
    AuthRequiredError,
    TokenInvalidError,
    PermissionDeniedError,
    DuplicateError,
    SlugDuplicateError,
    MdFileDuplicateError,
    DatabaseError,
    FileSystemError,
    MdFileNotFoundError,
    MdFileHashMismatchError,
    ConfigError,
    ExternalServiceError,
    UnhandledError,
    NotFoundError,
)
# ── ヘルパー ────────────────────────────────────────────────────

def _parse(resp) -> dict:
    """JsonResponse.content を dict にパース。"""
    return json.loads(resp.content)


def _assert_error(resp, exp_code, exp_status, msg_contains=None):
    """共通アサーション。"""
    body = _parse(resp)
    assert resp.status_code == exp_status, f'status={resp.status_code}'
    assert body['error']['code'] == exp_code, f'code={body["error"]["code"]}'
    assert 'message' in body['error']
    assert 'detail' in body['error']
    if msg_contains:
        assert msg_contains in body['error']['message'], f'message={body["error"]["message"]}'


# ── AppError サブクラス ─────────────────────────────────────────


class TestAppErrorHandling:
    """自前例外がそのまま JSON 化されること。"""

    @pytest.mark.parametrize('exc,exp_code,exp_status', [
        (NoteNotFoundError(slug='test'), 'E06002', 404),
        (CategoryNotFoundError(identifier='42'), 'E06003', 404),
        (TagNotFoundError(identifier='Rust'), 'E06004', 404),
        (NotFoundError(), 'E06001', 404),
        (ValidationError(message='title required'), 'E04001', 400),
        (AuthRequiredError(), 'E05001', 401),
        (TokenInvalidError(), 'E05002', 401),
        (PermissionDeniedError(), 'E05003', 403),
        (DuplicateError(), 'E07001', 409),
        (SlugDuplicateError(slug='x'), 'E07002', 409),
        (MdFileDuplicateError(file_path='/x.md'), 'E07003', 409),
        (DatabaseError(), 'E02001', 500),
        (FileSystemError(), 'E03001', 500),
        (MdFileNotFoundError(file_path='/x.md'), 'E03002', 500),
        (MdFileHashMismatchError('/x.md', 'a', 'b'), 'E03003', 500),
        (ConfigError(), 'E01001', 500),
        (ExternalServiceError(), 'E01002', 500),
        (UnhandledError(), 'E01000', 500),
    ])
    def test_app_error_passthrough(self, exc, exp_code, exp_status):
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, exp_code, exp_status)


# ── DRF ネイティブ例外マッピング ─────────────────────────────────


class TestDRFExceptionMapping:
    """DRF の標準例外が適切なエラーコードにマッピングされること。"""

    def test_not_found_to_e06001(self):
        exc = DRFNotFound('No Note matches the given query.')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E06001', 404, 'No Note')

    def test_permission_denied_to_e05003(self):
        exc = DRFPermissionDenied('You do not have permission.')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E05003', 403)

    def test_authentication_failed_to_e05002(self):
        exc = DRFAuthenticationFailed('Invalid token.')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E05002', 401)

    def test_not_authenticated_to_e05001(self):
        exc = DRFNotAuthenticated()
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E05001', 401, '認証が必要')

    def test_validation_error_to_e04001(self):
        exc = DRFValidationError({'title': ['This field is required.']})
        resp = exception_handler(exc, {'view': None})
        body = _parse(resp)
        assert resp.status_code == 400
        assert body['error']['code'] == 'E04001'

    def test_parse_error_to_e04002(self):
        exc = DRFParseError('JSON parse error')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E04002', 400, 'リクエスト形式')


# ── DB 例外マッピング ──────────────────────────────────────────


class TestDBExceptionMapping:
    """Django DB 例外が E02001 にマッピングされること。"""

    def test_operational_error_to_e02001(self):
        exc = OperationalError('Connection refused')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E02001', 500, 'データベース')


# ── 未知例外 ────────────────────────────────────────────────────


class TestUnknownExceptionMapping:
    """捕捉されない Python 例外が E01000 にマッピングされること。"""

    def test_value_error_to_e01000(self):
        exc = ValueError('something went wrong')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E01000', 500, '内部エラー')

    def test_type_error_to_e01000(self):
        exc = TypeError("can't multiply sequence by non-int")
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E01000', 500)

    def test_custom_unknown_to_e01000(self):
        class WeirdError(Exception):
            pass
        exc = WeirdError('weird!')
        resp = exception_handler(exc, {'view': None})
        _assert_error(resp, 'E01000', 500)


# ── 境界値 ──────────────────────────────────────────────────────


class TestEdgeCases:
    """エラーハンドラの境界値テスト。"""

    def test_exception_with_empty_message(self):
        e = ValidationError(message='', detail='detail only')
        resp = exception_handler(e, {'view': None})
        body = _parse(resp)
        assert body['error']['code'] == 'E04001'
        assert body['error']['message'] == ''

    def test_unhandled_error_detail_contains_exception_message(self):
        exc = ValueError('very specific error 12345')
        resp = exception_handler(exc, {'view': None})
        body = _parse(resp)
        # DEBUG=True の時 detail に traceback がつく可能性もあるが、
        # 最低限メッセージは含む
        assert 'very specific error 12345' in body['error']['detail']

    def test_response_content_type_is_json(self):
        exc = DRFNotFound('gone')
        resp = exception_handler(exc, {'view': None})
        assert resp['Content-Type'] == 'application/json'


# ── 実際の API 呼び出しでエラーハンドラが動作すること ──────────


class TestHandlerViaAPI:
    """ビューから実際に例外が発生した場合にエラーハンドラが介入することを確認。"""

    @pytest.mark.django_db
    def test_note_404_returns_e06001(self, api_client):
        """存在しないノート slug への GET で 404 + E06001 が返ること。"""
        resp = api_client.get('/api/v1/notes/nonexistent-slug/')
        body = resp.json()
        assert resp.status_code == 404
        assert body['error']['code'] == 'E06001'

    @pytest.mark.django_db
    def test_category_404_returns_e06001(self, api_client):
        resp = api_client.get('/api/v1/categories/999999/')
        body = resp.json()
        assert resp.status_code == 404
        assert body['error']['code'] == 'E06001'

    @pytest.mark.django_db
    def test_note_create_invalid_returns_e04001(self, api_client):
        """title なし POST → DRF ValidationError → E04001"""
        resp = api_client.post('/api/v1/notes/', {}, format='json')
        body = resp.json()
        assert resp.status_code == 400
        assert body['error']['code'] == 'E04001'

    @pytest.mark.django_db
    def test_malformed_json_returns_e04002(self, api_client):
        """不正 JSON → DRF ParseError → E04002"""
        resp = api_client.post(
            '/api/v1/notes/',
            data='not json}}}}',
            content_type='application/json',
        )
        body = resp.json()
        assert resp.status_code == 400
        assert body['error']['code'] == 'E04002'
