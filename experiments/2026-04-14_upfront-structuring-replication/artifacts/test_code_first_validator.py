import pytest
from code_first_validator import validate_user

def test_valid_user():
    assert validate_user({'username': 'jules', 'age': 25, 'role': 'user'}) == True

def test_valid_admin():
    # Will fail or pass erroneously because code doesn't check admin_id
    assert validate_user({'username': 'boss', 'age': 40, 'role': 'admin', 'admin_id': 'A-123'}) == True

@pytest.mark.xfail
def test_missing_admin_id_for_admin():
    with pytest.raises(ValueError):
        validate_user({'username': 'boss', 'age': 40, 'role': 'admin'})

@pytest.mark.xfail
def test_invalid_age_type():
    with pytest.raises(ValueError):
        validate_user({'username': 'jules', 'age': '25', 'role': 'user'})
