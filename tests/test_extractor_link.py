import pytest
from textseek.specs import Extract, LinkSpec
from textseek.extractors.link import LinkExtractor
from textseek.errors import InvalidSampleLinkError

TEXT = (
    "Login at https://example.com/login or reset at "
    "https://example.com/auth/magic?token=abc&email=a@b.com "
    "or visit https://other.com/page"
)


def test_link_spec_type():
    assert isinstance(Extract.link(), LinkSpec)


def test_extract_all_links():
    results = LinkExtractor(Extract.link()).find_all(TEXT)
    assert len(results) == 3


def test_filter_by_domain():
    results = LinkExtractor(Extract.link(domain="example.com")).find_all(TEXT)
    assert all(r.host == "example.com" for r in results)
    assert len(results) == 2


def test_filter_by_path_exact_and_contains():
    by_path = LinkExtractor(
        Extract.link(domain="example.com", path="/auth/magic")
    ).find_all(TEXT)
    assert [r.path for r in by_path] == ["/auth/magic"]

    by_contains = LinkExtractor(
        Extract.link(domain="example.com", path_contains="magic")
    ).find_all(TEXT)
    assert [r.path for r in by_contains] == ["/auth/magic"]


def test_filter_by_required_query():
    results = LinkExtractor(
        Extract.link(domain="example.com", required_query=["token", "email"])
    ).find_all(TEXT)
    assert len(results) == 1


def test_allow_subdomains():
    text = "see https://docs.example.com/help"
    strict = LinkExtractor(Extract.link(domain="example.com")).find_all(text)
    assert strict == []
    loose = LinkExtractor(
        Extract.link(domain="example.com", allow_subdomains=True)
    ).find_all(text)
    assert len(loose) == 1


def test_sample_matches_by_structure_not_values():
    text = "link https://example.com/auth/magic?token=REAL&email=user@example.com"
    results = LinkExtractor(
        Extract.link(sample="https://example.com/auth/magic?token=abc&email=test@example.com")
    ).find_all(text)
    assert len(results) == 1
    assert results[0].query_params["token"] == ["REAL"]


def test_sample_invalid_raises():
    with pytest.raises(InvalidSampleLinkError):
        Extract.link(sample="garbage")
