from textseek.extractors.base import Extractor
from textseek.results import CodeResult


class _Dummy:
    def find_all(self, text: str) -> list[CodeResult]:
        return [CodeResult(value=text, start=0, end=len(text))]


def test_dummy_satisfies_protocol():
    d: Extractor = _Dummy()
    assert isinstance(d, Extractor)
    assert d.find_all("hi")[0].value == "hi"
