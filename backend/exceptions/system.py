"""
システム例外（500系）

DB障害、ファイルIO障害、設定不正、外部サービス障害など、
ユーザー操作では回復不能なサーバー側エラー。
"""

from .base import AppError


class SystemError(AppError):
    """システム例外の基底クラス。http_status=500。"""
    pass


class UnhandledError(SystemError):
    """捕捉されなかった Python 例外。E01000。"""
    def __init__(self, detail='', original_type=''):
        msg = 'サーバー内部エラーが発生しました'
        super().__init__(code='E01000', message=msg, detail=detail, http_status=500)
        self.original_type = original_type


class ConfigError(SystemError):
    """設定不正。E01001。"""
    def __init__(self, message='設定に誤りがあります', detail=''):
        super().__init__(code='E01001', message=message, detail=detail, http_status=500)


class ExternalServiceError(SystemError):
    """外部サービス障害。E01002。"""
    def __init__(self, message='外部サービスとの通信に失敗しました', detail=''):
        super().__init__(code='E01002', message=message, detail=detail, http_status=500)


class DatabaseError(SystemError):
    """DB接続・クエリ失敗。E02001。"""
    def __init__(self, message='データベースエラーが発生しました', detail=''):
        super().__init__(code='E02001', message=message, detail=detail, http_status=500)


class FileSystemError(SystemError):
    """
    ファイルIO障害。E03001。
    MDファイルの読み書き失敗時に使う。
    """
    def __init__(self, message='ファイル操作に失敗しました', detail=''):
        super().__init__(code='E03001', message=message, detail=detail, http_status=500)


class MdFileNotFoundError(SystemError):
    """MD実体ファイルがストレージ上に見つからない。E03002。"""
    def __init__(self, file_path='', detail=''):
        msg = f'マークダウンファイルが見つかりません: {file_path}' if file_path else 'マークダウンファイルが見つかりません'
        super().__init__(code='E03002', message=msg, detail=detail or msg, http_status=500)


class MdFileHashMismatchError(SystemError):
    """DB上の file_hash と実体ファイルのハッシュが一致しない。E03003。"""
    def __init__(self, file_path='', expected='', actual=''):
        msg = f'ファイル整合性エラー: {file_path} (DB={expected}, FS={actual})'
        super().__init__(code='E03003', message='ファイル整合性エラー', detail=msg, http_status=500)
