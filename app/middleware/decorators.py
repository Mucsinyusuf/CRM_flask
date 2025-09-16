from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(*roles):
    """Require that the JWT contains a `role` claim in `roles`."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Ensure JWT is valid
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get('role')  # role must be a string
            
            if isinstance(role, str) and role in roles:
                return fn(*args, **kwargs)
            
            return jsonify({'msg': 'Forbidden - insufficient role'}), 403
        return decorator
    return wrapper

def roles_required(roles):
    """Alias that accepts a list/iterable of roles."""
    return role_required(*roles)
