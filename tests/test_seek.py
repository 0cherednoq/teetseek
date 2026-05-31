import pytest
from textseek.seek import TextSeek
from textseek.specs import Extract
from textseek.errors import ExtractNotFoundError, InvalidExtractSpecError


def test_extract_one_returns_result():
    seek = TextSeek("Your code is 123456")
    assert seek.extract_one(Extract.code(length=6)).value == "123456"


def test_extract_one_raises_when_absent():
    seek = TextSeek("no code")
    with pytest.raises(ExtractNotFoundError):
        seek.extract_one(Extract.code(length=6))


def test_extract_first_returns_none_when_absent():
    seek = TextSeek("no code")
    assert seek.extract_first(Extract.code(length=6)) is None


def test_extract_all_returns_list():
    seek = TextSeek("1234 5678")
    assert [r.value for r in seek.extract_all(Extract.code(length=4))] == ["1234", "5678"]


def test_contains():
    seek = TextSeek("code 4321")
    assert seek.contains(Extract.code(length=4)) is True
    assert seek.contains(Extract.code(length=9)) is False


def test_unknown_spec_raises():
    seek = TextSeek("x")
    with pytest.raises(InvalidExtractSpecError):
        seek.extract_all(object())  # type: ignore[arg-type]


def test_extract_first_and_contains_with_link():
    seek = TextSeek("visit https://example.com/login now")
    first = seek.extract_first(Extract.link())
    assert first is not None
    assert first.domain == "example.com"
    assert seek.contains(Extract.link(domain="example.com")) is True
    assert seek.contains(Extract.link(domain="absent.com")) is False


def test_extract_first_and_contains_with_regex():
    seek = TextSeek("pin 4321 ok")
    first = seek.extract_first(Extract.regex(r"\d{4}"))
    assert first is not None
    assert first.value == "4321"
    assert seek.contains(Extract.regex(r"\d{4}")) is True
    assert seek.contains(Extract.regex(r"ZZZ")) is False


def test_extract_one_with_regex_raises_when_absent():
    seek = TextSeek("no digits here")
    with pytest.raises(ExtractNotFoundError):
        seek.extract_one(Extract.regex(r"\d{4}"))
