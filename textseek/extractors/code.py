import re

from ..patterns import DEFAULT_SYMBOLS, build_code_pattern
from ..results import CodeResult
from ..specs import CodeSpec


class CodeExtractor:
    def __init__(self, spec: CodeSpec) -> None:
        self.spec = spec
        self.pattern = build_code_pattern(spec)

    def find_all(self, text: str) -> list[CodeResult]:
        if self.spec.near is not None:
            return self._find_near(text)
        return [
            CodeResult(value=m.group(), start=m.start(), end=m.end())
            for m in self.pattern.finditer(text)
            if self._passes(m.group())
        ]

    def _passes(self, token: str) -> bool:
        spec = self.spec
        if not spec.require_each_type:
            return True
        if spec.digits and not any(c.isdigit() for c in token):
            return False
        if spec.alphabet and not any(c.isalpha() for c in token):
            return False
        if spec.symbols and not any(c in DEFAULT_SYMBOLS for c in token):
            return False
        return True

    def _find_near(self, text: str) -> list[CodeResult]:
        spec = self.spec
        assert spec.near is not None
        idx = text.lower().find(spec.near.lower())
        if idx == -1:
            return []
        phrase_start = idx
        phrase_end = idx + len(spec.near)
        win_start = max(0, phrase_start - spec.window)
        win_end = min(len(text), phrase_end + spec.window)

        matches = [
            CodeResult(value=m.group(), start=m.start(), end=m.end())
            for m in self.pattern.finditer(text)
            if self._passes(m.group()) and win_start <= m.start() < win_end
        ]
        matches.sort(key=lambda r: _gap(r, phrase_start, phrase_end))
        return matches


def _gap(result: CodeResult, phrase_start: int, phrase_end: int) -> int:
    if result.start >= phrase_end:
        return result.start - phrase_end
    if result.end <= phrase_start:
        return phrase_start - result.end
    return 0
