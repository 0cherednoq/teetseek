from textseek.specs import Extract
from textseek.patterns import build_code_pattern, DEFAULT_SYMBOLS


def test_digits_exact_length_strict_boundaries():
    pat = build_code_pattern(Extract.code(length=6, digits=True))
    assert pat.search("code 123456 end").group() == "123456"
    # 6 digits inside a longer run must NOT match
    assert pat.search("1234567890") is None


def test_alphanumeric_range():
    pat = build_code_pattern(Extract.code(min_length=4, max_length=8, digits=True, alphabet=True))
    assert pat.search("token A1B2C3 here").group() == "A1B2C3"


def test_symbols_included():
    pat = build_code_pattern(Extract.code(length=9, digits=True, alphabet=True, symbols=True))
    assert pat.search("code A8F3-K2P9.").group() == "A8F3-K2P9"


def test_uppercase_only():
    pat = build_code_pattern(Extract.code(length=4, digits=False, alphabet=True, lowercase=False))
    assert pat.search("xx ABCD yy").group() == "ABCD"
    assert pat.search("abcd") is None


def test_custom_pattern_passthrough():
    pat = build_code_pattern(Extract.code(pattern=r"\d{3}"))
    assert pat.search("ab 123 cd").group() == "123"


def test_default_symbols_value():
    assert set(DEFAULT_SYMBOLS) == {"-", "_"}
