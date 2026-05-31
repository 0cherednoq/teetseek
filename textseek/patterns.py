import re

from .specs import CodeSpec

DEFAULT_SYMBOLS = "-_"


def _char_class(spec: CodeSpec) -> str:
    parts = ""
    if spec.digits:
        parts += "0-9"
    if spec.alphabet:
        if spec.uppercase:
            parts += "A-Z"
        if spec.lowercase:
            parts += "a-z"
    if spec.symbols:
        parts += re.escape(DEFAULT_SYMBOLS)
    return f"[{parts}]"


def _quantifier(spec: CodeSpec) -> str:
    if spec.length is not None:
        return f"{{{spec.length}}}"
    lo = spec.min_length if spec.min_length is not None else 1
    hi = spec.max_length if spec.max_length is not None else ""
    return f"{{{lo},{hi}}}"


def build_code_pattern(spec: CodeSpec) -> re.Pattern[str]:
    """Строит regex для поиска кодов.

    Returns:
        Скомпилированный паттерн. Совпадение — максимальный «токен» из
        разрешённых символов нужной длины, ограниченный символами не из
        класса (строгие границы). Проверка require_each_type выполняется
        пост-фильтром в экстракторе, не здесь.
    """
    if spec.pattern is not None:
        return re.compile(spec.pattern)
    cls = _char_class(spec)
    quant = _quantifier(spec)
    return re.compile(f"(?<!{cls}){cls}{quant}(?!{cls})")
