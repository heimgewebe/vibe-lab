import pytest
from test_first_validator import validate_user

def test_valid_user():
    assert validate_user({'username': 'jules', 'age': 25, 'role': 'user'}) == True

def test_valid_admin():
    assert validate_user({'username': 'boss', 'age': 40, 'role': 'admin', 'admin_id': 'A-123'}) == True

def test_missing_admin_id_for_admin():
    with pytest.raises(ValueError):
        validate_user({'username': 'boss', 'age': 40, 'role': 'admin'})

def test_invalid_age_type():
    with pytest.raises(ValueError):
        validate_user({'username': 'jules', 'age': '25', 'role': 'user'})
