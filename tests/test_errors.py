import pytest
from textseek.errors import (
    TextSeekError,
    ExtractNotFoundError,
    InvalidExtractSpecError,
    InvalidSampleLinkError,
    InvalidCodeSpecError,
    RegexExtractError,
)


@pytest.mark.parametrize("err", [
    ExtractNotFoundError,
    InvalidExtractSpecError,
    InvalidSampleLinkError,
    InvalidCodeSpecError,
    RegexExtractError,
])
def test_all_errors_subclass_base(err):
    assert issubclass(err, TextSeekError)
    assert issubclass(TextSeekError, Exception)
