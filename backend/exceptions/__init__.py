"""
Tech-Wiki 全例外のエクスポート

使用方法:
    from exceptions import (
        AppError,
        SystemError, UnhandledError, ConfigError, ExternalServiceError,
        DatabaseError, FileSystemError, MdFileNotFoundError, MdFileHashMismatchError,
        BusinessError, ValidationError,
        AuthRequiredError, TokenInvalidError, PermissionDeniedError,
        NotFoundError, NoteNotFoundError, CategoryNotFoundError, TagNotFoundError,
        DuplicateError, SlugDuplicateError, MdFileDuplicateError,
    )
"""

from .base import AppError

from .system import (
    SystemError,
    UnhandledError,
    ConfigError,
    ExternalServiceError,
    DatabaseError,
    FileSystemError,
    MdFileNotFoundError,
    MdFileHashMismatchError,
)

from .business import (
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

__all__ = [
    'AppError',
    'SystemError',
    'UnhandledError',
    'ConfigError',
    'ExternalServiceError',
    'DatabaseError',
    'FileSystemError',
    'MdFileNotFoundError',
    'MdFileHashMismatchError',
    'BusinessError',
    'ValidationError',
    'AuthRequiredError',
    'TokenInvalidError',
    'PermissionDeniedError',
    'NotFoundError',
    'NoteNotFoundError',
    'CategoryNotFoundError',
    'TagNotFoundError',
    'DuplicateError',
    'SlugDuplicateError',
    'MdFileDuplicateError',
]
