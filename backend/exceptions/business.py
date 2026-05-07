"""
業務例外（400系 / 404系 / 409系）

バリデーション失敗、認証エラー、リソース不在、重複など、
ユーザー操作やデータ内容に起因するエラー。
"""

from .base import AppError


class BusinessError(AppError):
    """業務例外の基底クラス。http_status はサブクラスが決定。"""
    pass


class ValidationError(BusinessError):
    """バリデーション失敗。E04001（400）。"""
    def __init__(self, message='入力内容に誤りがあります', detail=''):
        super().__init__(code='E04001', message=message, detail=detail, http_status=400)


class AuthRequiredError(BusinessError):
    """認証必須。E05001（401）。"""
    def __init__(self, message='認証が必要です', detail=''):
        super().__init__(code='E05001', message=message, detail=detail, http_status=401)


class TokenInvalidError(BusinessError):
    """トークン無効/期限切れ。E05002（401）。"""
    def __init__(self, message='トークンが無効です', detail=''):
        super().__init__(code='E05002', message=message, detail=detail, http_status=401)


class PermissionDeniedError(BusinessError):
    """権限不足。E05003（403）。"""
    def __init__(self, message='権限が不足しています', detail=''):
        super().__init__(code='E05003', message=message, detail=detail, http_status=403)


class NotFoundError(BusinessError):
    """
    リソース不在。E06001（404）。

    code パラメータを公開しており、サブクラスが上書き可能。
    """
    def __init__(self, message='リソースが見つかりません', detail='', code='E06001'):
        super().__init__(code=code, message=message, detail=detail, http_status=404)


class NoteNotFoundError(NotFoundError):
    """ノート不在。E06002（404）。"""
    def __init__(self, slug='', detail=''):
        msg = f'ノートが見つかりません: {slug}' if slug else 'ノートが見つかりません'
        super().__init__(code='E06002', message=msg, detail=detail or msg)


class CategoryNotFoundError(NotFoundError):
    """カテゴリ不在。E06003（404）。"""
    def __init__(self, identifier='', detail=''):
        msg = f'カテゴリが見つかりません: {identifier}' if identifier else 'カテゴリが見つかりません'
        super().__init__(code='E06003', message=msg, detail=detail or msg)


class TagNotFoundError(NotFoundError):
    """タグ不在。E06004（404）。"""
    def __init__(self, identifier='', detail=''):
        msg = f'タグが見つかりません: {identifier}' if identifier else 'タグが見つかりません'
        super().__init__(code='E06004', message=msg, detail=detail or msg)


class DuplicateError(BusinessError):
    """
    重複リソース。E07001（409）。

    code パラメータを公開しており、サブクラスが上書き可能。
    """
    def __init__(self, message='リソースが重複しています', detail='', code='E07001'):
        super().__init__(code=code, message=message, detail=detail, http_status=409)


class SlugDuplicateError(DuplicateError):
    """slug 重複。E07002（409）。"""
    def __init__(self, slug='', detail=''):
        msg = f'slug が重複しています: {slug}' if slug else 'slug が重複しています'
        super().__init__(code='E07002', message=msg, detail=detail or msg)


class MdFileDuplicateError(DuplicateError):
    """MDファイル実体の競合。E07003（409）。"""
    def __init__(self, file_path='', detail=''):
        msg = f'同名ファイルが既に存在します: {file_path}' if file_path else '同名ファイルが既に存在します'
        super().__init__(code='E07003', message=msg, detail=detail or msg)
