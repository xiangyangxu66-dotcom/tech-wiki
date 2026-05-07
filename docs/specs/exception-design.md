# 例外設計書 (Exception Design)

> **対象読者:** バックエンド開発者。
> **関連:** エラーコード定義は `docs/specs/error-codes.md` 参照。

---

## 設計方針

1. **例外はコードの近くで投げ、ハンドラで一元整形する**
   - 各 ViewSet / Service 層で適切な AppError サブクラスを `raise`
   - DRF の `EXCEPTION_HANDLER`（`config/error_handler.py`）で全例外を JSON 形式に変換
   - ビジネスロジック層に HTTP の知識（JsonResponse 等）を漏らさない

2. **システム例外と業務例外を分離する**
   - システム例外（5xx）→ ログに詳細を残し、ユーザーには「サーバーエラー」のみ返す
   - 業務例外（4xx）→ ユーザーが行動して解決できる情報を返す

3. **エラーコードは変更しない**
   - 一度割り当てたコードはリサイクルしない
   - 新しいエラーコードは必ず `error-codes.md` に追記し、フロント担当者と合意する

---

## 例外階層

```
AppError (base)                             ← backend/exceptions/base.py
├── SystemError (500系)                     ← backend/exceptions/system.py
│   ├── UnhandledError        E01000
│   ├── ConfigError           E01001
│   ├── ExternalServiceError  E01002
│   ├── DatabaseError         E02001
│   ├── FileSystemError       E03001
│   ├── MdFileNotFoundError   E03002
│   └── MdFileHashMismatchError E03003
│
└── BusinessError (400系)                   ← backend/exceptions/business.py
    ├── ValidationError       E04001
    ├── AuthRequiredError     E05001
    ├── TokenInvalidError     E05002
    ├── PermissionDeniedError E05003
    ├── NotFoundError         E06001
    │   ├── ArticleNotFoundError E06002
    │   ├── CategoryNotFoundError E06003
    │   └── TagNotFoundError     E06004
    └── DuplicateError        E07001
        ├── SlugDuplicateError    E07002
        └── MdFileDuplicateError  E07003
```

---

## 使い方

### ViewSet / Service 層での送出

```python
from exceptions import (
    ArticleNotFoundError,
    ValidationError,
    PermissionDeniedError,
    MdFileNotFoundError,
    SlugDuplicateError,
)

class ArticleViewSet(viewsets.ModelViewSet):
    def retrieve(self, request, slug=None):
        article = get_object_or_404(Article, slug=slug)
        # ↑ これは DRF の NotFound を投げるので error_handler が E06001 に変換する
        return Response(...)

    def perform_create(self, serializer):
        # Slug重複チェック（save前に確実に検知したい場合）
        slug = serializer.validated_data.get('slug')
        if Article.objects.filter(slug=slug).exists():
            raise SlugDuplicateError(slug=slug)

        # ファイル書き込み
        try:
            write_md_file(path, content)
        except IOError as e:
            raise FileSystemError(detail=str(e))

        serializer.save(...)
```

### カスタムバリデーション

```python
# DRF Serializer の validate_xxx 内で
from exceptions import ValidationError

class ArticleSerializer(serializers.ModelSerializer):
    def validate_title(self, value):
        if len(value) > 500:
            raise ValidationError(
                message='タイトルは500文字以内にしてください',
                detail=f'title length={len(value)}'
            )
        return value
```

> **注意:** Serializer の `validate_xxx` 内で直接 `ValidationError` を投げるのは **非推奨**。
> DRF 標準の `serializers.ValidationError` を使えば、エラーハンドラが E04001 にマッピングする。
> 明示的にエラーコードを指定したい場合のみ、自前の `ValidationError` を使う。

---

## ハンドラの動作

`config/error_handler.py` の `exception_handler()` は以下の優先順位で処理する：

| 優先度 | 例外タイプ | 変換先 |
|--------|-----------|--------|
| 1 | `AppError` サブクラス | 例外自身の code/message/detail/http_status をそのまま JSON 化 |
| 2 | DRF `NotFound` | E06001 |
| 3 | DRF `PermissionDenied` | E05003 |
| 4 | DRF `AuthenticationFailed` | E05002 |
| 5 | DRF `NotAuthenticated` | E05001 |
| 6 | DRF `ValidationError` | E04001 |
| 7 | DRF `ParseError` | E04002 |
| 8 | Django `OperationalError` | E02001 |
| 9 | その他 Python 例外 | E01000（logging + DEBUG時にスタックトレース付与） |

---

## テスト方針

### 単体テスト

```python
from exceptions import ValidationError, ArticleNotFoundError

# 例外が正しく構築できること
e = ArticleNotFoundError(slug='no-such-article')
assert e.code == 'E06002'
assert e.http_status == 404
assert 'no-such-article' in e.message

d = e.to_dict()
assert d['error']['code'] == 'E06002'
```

### 結合テスト（APIレベル）

```python
def test_article_not_found_returns_404(api_client):
    resp = api_client.get('/api/v1/articles/non-existent-slug/')
    assert resp.status_code == 404
    body = resp.json()
    assert body['error']['code'] == 'E06001'  # or 'E06002'
    assert 'message' in body['error']
```

### ハンドラテスト

```python
# ハンドラ単体で、各例外タイプが期待する JSON 形式を返すことを確認
from config.error_handler import exception_handler
from django.test import RequestFactory

def test_drf_not_found_mapped_to_e06001():
    exc = DRFNotFound('No Article matches the given query.')
    resp = exception_handler(exc, {'view': None})
    assert resp.status_code == 404
    assert resp.data == {
        'error': {
            'code': 'E06001',
            'message': 'No Article matches the given query.',
            'detail': 'No Article matches the given query.',
        }
    }
```

---

## 追加ルール

1. **新しいエラーコードを追加する時**
   - 必ず `docs/specs/error-codes.md` を更新する
   - フロントエンド担当者に通知し、画面挙動の合意を得る

2. **エラーコードを削除してはいけない**
   - フロントエンドが特定コードに依存している可能性があるため
   - 非推奨にする場合はコメントで `# DEPRECATED: use E0xxxx` と明記

3. **AppError の階層に収まらない例外は追加しない**
   - 必要なら `BusinessError` か `SystemError` の新しいサブクラスを作る
   - `AppError` を直接継承した例外は作らない（必ず SystemError か BusinessError の下に作る）
