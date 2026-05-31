import pytest
from textseek.specs import Extract, RegexSpec
from textseek.errors import RegexExtractError


def test_regex_spec_created():
    spec = Extract.regex(r"Order:\s*(\d+)")
    assert isinstance(spec, RegexSpec)
    assert spec.pattern == r"Order:\s*(\d+)"
    assert spec.flags == 0


def test_regex_invalid_pattern_raises():
    with pytest.raises(RegexExtractError):
        Extract.regex(r"(unbalanced")
