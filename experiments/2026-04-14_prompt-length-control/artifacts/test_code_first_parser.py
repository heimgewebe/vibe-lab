import pytest
from code_first_parser import extract_bold_text

def test_basic_bold():
    assert extract_bold_text("Here is some **bold text**.") == ["bold text"]

def test_escaped_stars_ignored():
    assert extract_bold_text(r"Here is some \*\*not bold\*\* but this is **bold**.") == ["bold"]

def test_unmatched_bold_with_escaped():
    assert extract_bold_text(r"This is **bold \*\* and more bold**.") == [r"bold \*\* and more bold"]

def test_stars_inside_bold_no_match():
    assert extract_bold_text(r"This **should fail \*\* because of escape**.") == [r"should fail \*\* because of escape"]

def test_fail_on_escape_in_end():
    # If the text is **bold\**, it should NOT be extracted because the end is escaped.
    assert extract_bold_text(r"This is **not bold\**.") == []
