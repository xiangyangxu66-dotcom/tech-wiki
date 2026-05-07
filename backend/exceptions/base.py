"""
Tech-Wiki 例外基底クラス

階層:
    AppError (基底)
    ├── SystemError (500系)
    └── BusinessError (400系/404系)

全例外は code / message / detail / http_status の4属性を持ち、
ハンドラで統一 JSON 形式に変換される。
"""


class AppError(Exception):
    """
    アプリケーション全体の基底例外。

    Attributes:
        code (str):   エラーコード（E01xxx - E07xxx）
        message (str): ユーザー向けメッセージ（日本語）
        detail (str):  開発者向け詳細（スタックトレースやデバッグ情報）
        http_status (int): HTTP ステータスコード
    """

    def __init__(self, code, message, detail='', http_status=500):
        self.code = code
        self.message = message
        self.detail = detail or message
        self.http_status = http_status
        super().__init__(message)

    def to_dict(self):
        """
        統一エラー形式の dict を返す。

        Returns:
            dict: {"error": {"code": ..., "message": ..., "detail": ...}}
        """
        return {
            'error': {
                'code': self.code,
                'message': self.message,
                'detail': self.detail,
            }
        }

    def __repr__(self):
        return f'{self.__class__.__name__}(code={self.code}, message={self.message!r})'
