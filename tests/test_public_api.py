import textseek
from textseek import (
    TextSeek,
    Extract,
    CodeResult,
    LinkResult,
    RegexResult,
    TextSeekError,
    ExtractNotFoundError,
    InvalidExtractSpecError,
    InvalidSampleLinkError,
    InvalidCodeSpecError,
    RegexExtractError,
)


def test_top_level_example_from_spec():
    text = "Your verification code is 123456"
    result = TextSeek(text).extract_one(Extract.code(length=6, digits=True))
    assert result.value == "123456"


def test_all_exports_present():
    for name in [
        "TextSeek", "Extract",
        "CodeResult", "LinkResult", "RegexResult",
        "TextSeekError", "ExtractNotFoundError", "InvalidExtractSpecError",
        "InvalidSampleLinkError", "InvalidCodeSpecError", "RegexExtractError",
    ]:
        assert name in textseek.__all__
