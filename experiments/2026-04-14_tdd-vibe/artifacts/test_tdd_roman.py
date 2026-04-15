import pytest
from tdd_roman import roman_to_int

def test_roman_to_int_basic():
    assert roman_to_int("III") == 3
    assert roman_to_int("LVIII") == 58
    assert roman_to_int("MCMXCIV") == 1994

def test_invalid_chars():
    with pytest.raises(ValueError):
        roman_to_int("A")

def test_invalid_repetition_four_times():
    # I, X, C, M can be repeated max 3 times
    with pytest.raises(ValueError, match="Invalid roman numeral: too many consecutive identical characters"):
        roman_to_int("IIII")
    with pytest.raises(ValueError):
        roman_to_int("XXXX")

def test_invalid_repetition_v_l_d():
    # V, L, D can never be repeated
    with pytest.raises(ValueError, match="Invalid roman numeral: V, L, D cannot be repeated"):
        roman_to_int("VV")
    with pytest.raises(ValueError):
        roman_to_int("LL")

def test_invalid_subtraction():
    # I can only precede V and X.
    # X can only precede L and C.
    # C can only precede D and M.
    # V, L, D can never be subtracted.
    with pytest.raises(ValueError, match="Invalid roman numeral: invalid subtraction"):
        roman_to_int("IC")
    with pytest.raises(ValueError):
        roman_to_int("VX")
