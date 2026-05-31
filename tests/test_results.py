import pytest
from textseek.results import CodeResult, LinkResult, RegexResult


def test_code_result_fields_and_frozen():
    r = CodeResult(value="123456", start=5, end=11)
    assert (r.value, r.start, r.end) == ("123456", 5, 11)
    with pytest.raises(AttributeError):
        r.value = "x"


def test_link_result_fields():
    r = LinkResult(
        value="https://example.com/a?x=1",
        start=0, end=25,
        scheme="https", domain="example.com", host="example.com",
        port=None, path="/a", query="x=1", fragment="",
        query_params={"x": ["1"]},
    )
    assert r.domain == "example.com"
    assert r.query_params["x"] == ["1"]


def test_regex_result_fields():
    r = RegexResult(value="A1", start=0, end=2, groups=("A1",), groupdict={})
    assert r.value == "A1"
    assert r.groups == ("A1",)
