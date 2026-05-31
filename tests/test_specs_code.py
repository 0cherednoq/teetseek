import pytest
from textseek.specs import Extract, CodeSpec
from textseek.errors import InvalidCodeSpecError


def test_code_defaults():
    spec = Extract.code(length=6)
    assert isinstance(spec, CodeSpec)
    assert spec.length == 6
    assert spec.digits is True
    assert spec.alphabet is False
    assert spec.window == 300


def test_code_length_with_range_raises():
    with pytest.raises(InvalidCodeSpecError):
        Extract.code(length=6, min_length=4)


def test_code_min_gt_max_raises():
    with pytest.raises(InvalidCodeSpecError):
        Extract.code(min_length=8, max_length=4)


def test_code_no_char_type_raises():
    with pytest.raises(InvalidCodeSpecError):
        Extract.code(length=6, digits=False, alphabet=False, symbols=False)


def test_code_alphabet_without_case_raises():
    with pytest.raises(InvalidCodeSpecError):
        Extract.code(length=6, alphabet=True, uppercase=False, lowercase=False)


def test_code_pattern_skips_char_type_validation():
    spec = Extract.code(digits=False, alphabet=False, symbols=False, pattern=r"\d{6}")
    assert spec.pattern == r"\d{6}"
