from typing import overload

from .errors import ExtractNotFoundError, InvalidExtractSpecError
from .extractors.base import Extractor
from .extractors.code import CodeExtractor
from .extractors.link import LinkExtractor
from .extractors.regex import RegexExtractor
from .results import CodeResult, ExtractResult, LinkResult, RegexResult
from .specs import CodeSpec, ExtractSpec, LinkSpec, RegexSpec


class TextSeek:
    def __init__(self, text: str) -> None:
        self.text = text

    def _extractor(self, spec: ExtractSpec) -> Extractor:
        if isinstance(spec, CodeSpec):
            return CodeExtractor(spec)
        if isinstance(spec, LinkSpec):
            return LinkExtractor(spec)
        if isinstance(spec, RegexSpec):
            return RegexExtractor(spec)
        raise InvalidExtractSpecError(f"Неизвестная спецификация: {spec!r}")

    @overload
    def extract_all(self, spec: CodeSpec) -> list[CodeResult]: ...
    @overload
    def extract_all(self, spec: LinkSpec) -> list[LinkResult]: ...
    @overload
    def extract_all(self, spec: RegexSpec) -> list[RegexResult]: ...

    def extract_all(self, spec: ExtractSpec) -> list[ExtractResult]:
        return self._extractor(spec).find_all(self.text)

    @overload
    def extract_first(self, spec: CodeSpec) -> CodeResult | None: ...
    @overload
    def extract_first(self, spec: LinkSpec) -> LinkResult | None: ...
    @overload
    def extract_first(self, spec: RegexSpec) -> RegexResult | None: ...

    def extract_first(self, spec: ExtractSpec) -> ExtractResult | None:
        results = self.extract_all(spec)
        return results[0] if results else None

    @overload
    def extract_one(self, spec: CodeSpec) -> CodeResult: ...
    @overload
    def extract_one(self, spec: LinkSpec) -> LinkResult: ...
    @overload
    def extract_one(self, spec: RegexSpec) -> RegexResult: ...

    def extract_one(self, spec: ExtractSpec) -> ExtractResult:
        result = self.extract_first(spec)
        if result is None:
            raise ExtractNotFoundError("Совпадение не найдено")
        return result

    def contains(self, spec: ExtractSpec) -> bool:
        return self.extract_first(spec) is not None
