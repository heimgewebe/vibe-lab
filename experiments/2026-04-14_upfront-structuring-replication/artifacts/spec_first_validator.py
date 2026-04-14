def validate_user(data: dict) -> bool:
    """
    Spec-First Logic:
    - username: str, len >= 3
    - age: int, >= 18
    - role: str in ["user", "admin"]
    - if role == "admin", admin_id must exist, be str, and start with "A-"
    """
    if not isinstance(data.get('username'), str) or len(data['username']) < 3:
        raise ValueError("Invalid username")

    if not isinstance(data.get('age'), int) or data['age'] < 18:
        raise ValueError("Invalid age")

    role = data.get('role')
    if role not in ['user', 'admin']:
        raise ValueError("Invalid role")

    if role == 'admin':
        admin_id = data.get('admin_id')
        if not isinstance(admin_id, str) or not admin_id.startswith('A-'):
            raise ValueError("Invalid admin_id")

    return True
