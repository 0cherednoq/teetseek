import pytest
from textseek.links import find_link_candidates, parse_sample
from textseek.errors import InvalidSampleLinkError


def test_finds_links_with_offsets():
    text = "Open https://example.com/login or https://docs.example.com/help"
    links = find_link_candidates(text)
    assert [l.value for l in links] == [
        "https://example.com/login",
        "https://docs.example.com/help",
    ]
    assert text[links[0].start:links[0].end] == "https://example.com/login"


def test_parses_all_parts():
    text = "go https://example.com/auth/magic?token=abc123&email=test@example.com#top now"
    link = find_link_candidates(text)[0]
    assert link.scheme == "https"
    assert link.domain == "example.com"
    assert link.host == "example.com"
    assert link.port is None
    assert link.path == "/auth/magic"
    assert link.query == "token=abc123&email=test@example.com"
    assert link.fragment == "top"
    assert link.query_params == {"token": ["abc123"], "email": ["test@example.com"]}


def test_strips_trailing_punctuation():
    link = find_link_candidates("Visit https://example.com/page.")[0]
    assert link.value == "https://example.com/page"


def test_parse_sample_extracts_filters():
    scheme, domain, path, keys = parse_sample(
        "https://example.com/auth/magic?token=abc&email=test@example.com"
    )
    assert scheme == "https"
    assert domain == "example.com"
    assert path == "/auth/magic"
    assert set(keys) == {"token", "email"}


def test_parse_sample_invalid_raises():
    with pytest.raises(InvalidSampleLinkError):
        parse_sample("not a url")
