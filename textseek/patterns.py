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


def _type_lookaheads(spec: CodeSpec, all_class: str) -> str:
    """Returns lookahead assertions requiring each enabled type within the token.

    Uses the full character class to bound the scan so the lookahead cannot
    escape the current token.  When only one type is active no lookaheads are
    needed (every token trivially contains that type).
    """
    type_classes: list[str] = []
    if spec.digits:
        type_classes.append("[0-9]")
    if spec.alphabet:
        if spec.uppercase and spec.lowercase:
            type_classes.append("[A-Za-z]")
        elif spec.uppercase:
            type_classes.append("[A-Z]")
        else:
            type_classes.append("[a-z]")
    if spec.symbols:
        type_classes.append(f"[{re.escape(DEFAULT_SYMBOLS)}]")

    if len(type_classes) < 2:
        return ""

    # For each required type T, assert: scanning through allowed chars we can
    # find T before leaving the token.  Pattern: (?=all_class*T)
    # This fails at any position where the remainder of the token does NOT
    # contain T — which is exactly what we want.
    return "".join(f"(?={all_class}*{t})" for t in type_classes)


def build_code_pattern(spec: CodeSpec) -> re.Pattern[str]:
    """Строит regex для поиска кодов.

    Returns:
        Скомпилированный паттерн. Совпадение — максимальный «токен» из
        разрешённых символов нужной длины, ограниченный символами не из
        класса (строгие границы). Когда задано несколько типов символов,
        паттерн дополнительно требует присутствия каждого типа в токене.
    """
    if spec.pattern is not None:
        return re.compile(spec.pattern)
    cls = _char_class(spec)
    quant = _quantifier(spec)
    lookaheads = _type_lookaheads(spec, cls)
    return re.compile(f"(?<!{cls}){lookaheads}{cls}{quant}(?!{cls})")
