from textseek.specs import Extract
from textseek.extractors.code import CodeExtractor


def test_find_digits_returns_result_with_offsets():
    ex = CodeExtractor(Extract.code(length=6, digits=True))
    results = ex.find_all("Your code is 123456 thanks")
    assert len(results) == 1
    r = results[0]
    assert r.value == "123456"
    assert r.start == 13
    assert r.end == 19


def test_find_all_multiple():
    ex = CodeExtractor(Extract.code(length=4, digits=True))
    results = ex.find_all("1234 and 5678")
    assert [r.value for r in results] == ["1234", "5678"]


def test_require_each_type_filters_pure_digits():
    ex = CodeExtractor(
        Extract.code(length=8, digits=True, alphabet=True, require_each_type=True)
    )
    results = ex.find_all("12345678 ABCDEFGH A1B2C3D4")
    assert [r.value for r in results] == ["A1B2C3D4"]


def test_no_match_returns_empty():
    ex = CodeExtractor(Extract.code(length=6, digits=True))
    assert ex.find_all("no codes here") == []


def test_near_picks_code_next_to_phrase():
    text = (
        "Account number 99887766. "
        "Your verification code is 123456. "
        "Reference 55554444."
    )
    ex = CodeExtractor(
        Extract.code(length=6, digits=True, near="verification code", window=40)
    )
    results = ex.find_all(text)
    assert results[0].value == "123456"


def test_near_phrase_absent_returns_empty():
    ex = CodeExtractor(
        Extract.code(length=6, digits=True, near="verification code")
    )
    assert ex.find_all("just 123456 here") == []


def test_near_window_excludes_far_codes():
    text = "verification code: 123456" + (" " * 100) + "999999"
    ex = CodeExtractor(
        Extract.code(length=6, digits=True, near="verification code", window=20)
    )
    results = ex.find_all(text)
    assert [r.value for r in results] == ["123456"]


def test_near_ignores_phrase_word_that_is_itself_a_candidate():
    # "confirmation" (12 chars) is a valid min8-max12 alnum token and overlaps
    # the phrase "confirmation code"; it must NOT win over the real code after it.
    text = "Your confirmation code is A8F3-K2P9. Enter it soon."
    ex = CodeExtractor(
        Extract.code(
            min_length=8,
            max_length=12,
            digits=True,
            alphabet=True,
            symbols=True,
            near="confirmation code",
        )
    )
    results = ex.find_all(text)
    assert results[0].value == "A8F3-K2P9"
