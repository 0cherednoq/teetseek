from typing import Protocol, runtime_checkable

from ..results import ExtractResult


@runtime_checkable
class Extractor(Protocol):
    def find_all(self, text: str) -> list[ExtractResult]: ...
