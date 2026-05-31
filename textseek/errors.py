class TextSeekError(Exception):
    """Базовая ошибка библиотеки."""


class ExtractNotFoundError(TextSeekError):
    """Совпадение не найдено."""


class InvalidExtractSpecError(TextSeekError):
    """Некорректная спецификация поиска."""


class InvalidSampleLinkError(TextSeekError):
    """Некорректный пример ссылки."""


class InvalidCodeSpecError(TextSeekError):
    """Некорректные настройки поиска кода."""


class RegexExtractError(TextSeekError):
    """Ошибка при работе с regex."""
