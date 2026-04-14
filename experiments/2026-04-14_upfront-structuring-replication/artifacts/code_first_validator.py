def validate_user(data: dict) -> bool:
    if 'username' not in data or len(data['username']) < 3:
        raise ValueError("Invalid username")
    if 'age' not in data or data['age'] < 18:
        raise ValueError("Invalid age")
    if 'role' not in data or data['role'] not in ['user', 'admin']:
        raise ValueError("Invalid role")

    # Missing type checks (e.g. is 'age' actually an int or a string "25"?)
    # Missing conditional rule logic (if admin, check admin_id starts with A-)
    return True
