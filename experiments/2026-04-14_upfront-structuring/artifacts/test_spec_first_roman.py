import pytest
from spec_first_roman import roman_to_int

def test_roman_to_int_basic():
    assert roman_to_int("III") == 3
    assert roman_to_int("LVIII") == 58
    assert roman_to_int("MCMXCIV") == 1994

def test_invalid_chars():
    with pytest.raises(ValueError):
        roman_to_int("A")

def test_invalid_repetition():
    with pytest.raises(ValueError):
        roman_to_int("IIII")
    with pytest.raises(ValueError):
        roman_to_int("VV")

def test_invalid_subtraction():
    with pytest.raises(ValueError):
        roman_to_int("IC")
    with pytest.raises(ValueError):
        roman_to_int("VX")
