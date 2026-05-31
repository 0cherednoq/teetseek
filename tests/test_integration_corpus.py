import pytest
from textseek import TextSeek, Extract
from tests.corpus import CASES


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_corpus_code_extraction(case):
    _id, text, expected_code, code_kwargs, _link = case
    if expected_code is None:
        pytest.skip("no code in this case")
    result = TextSeek(text).extract_one(Extract.code(**code_kwargs))
    assert result.value == expected_code
    # offsets must point back at the value in the source text
    assert text[result.start:result.end] == expected_code


@pytest.mark.parametrize("case", CASES, ids=[c[0] for c in CASES])
def test_corpus_link_extraction(case):
    _id, text, _code, _kwargs, expected_link = case
    if expected_link is None:
        pytest.skip("no link in this case")
    result = TextSeek(text).extract_one(Extract.link())
    assert result.value == expected_link
