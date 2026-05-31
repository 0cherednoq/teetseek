from textseek.specs import Extract
from textseek.extractors.regex import RegexExtractor


def test_value_is_first_group_when_groups_present():
    ex = RegexExtractor(Extract.regex(r"Order ID:\s*([A-Z0-9\-]+)"))
    results = ex.find_all("Order ID: AB-123 done")
    assert results[0].value == "AB-123"
    assert results[0].groups == ("AB-123",)


def test_value_is_full_match_without_groups():
    ex = RegexExtractor(Extract.regex(r"\d{4}"))
    results = ex.find_all("pin 4321 ok")
    assert results[0].value == "4321"
    assert results[0].start == 4
    assert results[0].end == 8


def test_groupdict_named_groups():
    ex = RegexExtractor(Extract.regex(r"(?P<k>\w+)=(?P<v>\d+)"))
    results = ex.find_all("a=1")
    assert results[0].groupdict == {"k": "a", "v": "1"}


def test_no_match_returns_empty():
    ex = RegexExtractor(Extract.regex(r"\d{4}"))
    assert ex.find_all("none") == []
