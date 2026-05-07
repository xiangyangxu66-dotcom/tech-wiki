"""
Tech-Wiki カスタム例外ハンドラ

DRF の EXCEPTION_HANDLER に設定する。
全例外を統一 JSON 形式に変換し、フロントエンドがパースしやすい形で返す。

出力形式:
    {
        "error": {
            "code": "E04001",
            "message": "ユーザー向け日本語メッセージ",
            "detail": "開発者向け詳細（デバッグ用）"
        }
    }

DEBUG=True 時は detail にスタックトレースを含める。
"""

import logging
import traceback

from django.conf import settings
from django.http import JsonResponse, Http404 as DjangoHttp404
from django.db import OperationalError as DjangoDBError

from rest_framework.exceptions import (
    APIException as DRFAPIException,
    NotFound as DRFNotFound,
    PermissionDenied as DRFPermissionDenied,
    AuthenticationFailed as DRFAuthenticationFailed,
    ValidationError as DRFValidationError,
    ParseError as DRFParseError,
    NotAuthenticated as DRFNotAuthenticated,
)

from exceptions import AppError
from exceptions.system import UnhandledError, DatabaseError
from exceptions.business import (
    ValidationError,
    AuthRequiredError,
    TokenInvalidError,
    PermissionDeniedError,
    NotFoundError,
)

logger = logging.getLogger('wiki')


def exception_handler(exc, context):
    """
    Custom DRF exception handler.

    === 処理分岐 ===
    1. 自前の AppError サブクラス → そのまま JSON 化
    2. DRF ネイティブ例外 → 対応するエラーコードにマッピング
    3. Django DB 例外 (OperationalError, IntegrityError) → DatabaseError
    4. その他全例外 → UnhandledError (E01000)

    Args:
        exc: 発生した例外
        context: DRF のコンテキスト dict（view, args, kwargs, request を含む）

    Returns:
        JsonResponse or None (DRF に処理を委譲する場合)
    """
    # ── Case 1: Our AppError ──
    if isinstance(exc, AppError):
        return _to_response(exc.code, exc.message, exc.detail, exc.http_status)

    # ── Case 2: DRF native exceptions → mapped codes ──
    mapping = _get_drf_mapping()
    for drf_type, handler in mapping.items():
        if isinstance(exc, drf_type):
            return handler(exc)

    # ── Case 2b: Django Http404 (get_object_or_404) → E06001 ──
    if isinstance(exc, DjangoHttp404):
        return _to_response('E06001', str(exc), str(exc), 404)

    # ── Case 3: Django DB errors ──
    if isinstance(exc, DjangoDBError):
        dbe = DatabaseError(detail=str(exc))
        return _to_response(dbe.code, dbe.message, dbe.detail, dbe.http_status)

    # ── Case 4: Everything else → UnhandledError ──
    logger.exception(f"Unhandled exception in {context.get('view', '?')}: {exc}")

    debug_detail = str(exc)
    if settings.DEBUG:
        debug_detail += '\n' + traceback.format_exc()

    ue = UnhandledError(detail=debug_detail, original_type=type(exc).__name__)
    return _to_response(ue.code, ue.message, ue.detail, ue.http_status)


def _get_drf_mapping():
    """DRF 例外タイプ → ハンドラ関数 のマッピングを返す。"""
    return {
        DRFNotFound: lambda e: _to_response('E06001', str(e.detail), str(e.detail), 404),
        DRFPermissionDenied: lambda e: _to_response('E05003', str(e.detail), str(e.detail), 403),
        DRFAuthenticationFailed: lambda e: _to_response('E05002', str(e.detail), str(e.detail), 401),
        DRFNotAuthenticated: lambda e: _to_response('E05001', '認証が必要です', str(e.detail), 401),
        DRFValidationError: lambda e: _to_response('E04001', '入力内容に誤りがあります', str(e.detail), 400),
        DRFParseError: lambda e: _to_response('E04002', 'リクエスト形式が不正です', str(e.detail), 400),
    }


def _to_response(code, message, detail, http_status):
    """
    統一 JSON エラーレスポンスを構築。

    Args:
        code (str): エラーコード
        message (str): ユーザー向けメッセージ
        detail (str): 開発者向け詳細
        http_status (int): HTTP ステータスコード

    Returns:
        JsonResponse
    """
    payload = {
        'error': {
            'code': code,
            'message': str(message),
            'detail': str(detail),
        }
    }
    return JsonResponse(payload, status=http_status)
