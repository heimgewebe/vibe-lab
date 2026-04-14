import pytest
from baseline_roman import roman_to_int

def test_roman_to_int_basic():
    assert roman_to_int("III") == 3
    assert roman_to_int("LVIII") == 58
    assert roman_to_int("MCMXCIV") == 1994

def test_invalid_char():
    with pytest.raises(ValueError):
        roman_to_int("A")

def test_invalid_format_iiii():
    with pytest.raises(ValueError):
        roman_to_int("IIII")

def test_invalid_format_vv():
    with pytest.raises(ValueError):
        roman_to_int("VV")

def test_invalid_format_ic():
    with pytest.raises(ValueError):
        roman_to_int("IC")
