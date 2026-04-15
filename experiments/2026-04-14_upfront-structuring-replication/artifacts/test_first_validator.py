def validate_user(data: dict) -> bool:
    if not isinstance(data.get('username'), str) or len(data['username']) < 3:
        raise ValueError("Username must be a string of at least 3 characters")

    if type(data.get('age')) is not int or data['age'] < 18:
        raise ValueError("Age must be an integer >= 18")

    role = data.get('role')
    if role not in ('user', 'admin'):
        raise ValueError("Role must be user or admin")

    if role == 'admin':
        admin_id = data.get('admin_id')
        if type(admin_id) is not str or not admin_id.startswith('A-'):
            raise ValueError("Admin requires an admin_id starting with A-")

    return True
