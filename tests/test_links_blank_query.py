from textseek import TextSeek, Extract
from textseek.links import find_link_candidates, parse_sample


def test_blank_query_value_key_retained():
    link = find_link_candidates("see https://example.com/p?token=&email=a@b.com")[0]
    assert "token" in link.query_params
    assert link.query_params["token"] == [""]


def test_required_query_matches_blank_valued_param():
    text = "go https://example.com/p?token=&email=a@b.com here"
    results = TextSeek(text).extract_all(Extract.link(required_query=["token"]))
    assert len(results) == 1


def test_sample_keys_include_blank_valued_param():
    _scheme, _domain, _path, keys = parse_sample("https://example.com/p?token=&email=x@y.com")
    assert set(keys) == {"token", "email"}
