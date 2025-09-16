from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import User, Role
from flask_jwt_extended import create_access_token
from ..schemas import UserSchema

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

# ============================
# REGISTER
# ============================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role_name = data.get('role', 'User')  # default to seeded 'User' role

    if not username or not email or not password:
        return jsonify({'msg': 'username, email and password required'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'msg': 'user already exists'}), 400

    # Get the Role object
    role_obj = Role.query.filter_by(name=role_name).first()
    if not role_obj:
        return jsonify({'msg': f"Role '{role_name}' not found"}), 400

    # Create user with role_id
    u = User(username=username, email=email, role_id=role_obj.id)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()

    return jsonify({'msg': 'registered', 'user': user_schema.dump(u)}), 201


# ============================
# LOGIN
# ============================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'msg': 'username and password required'}), 400

    # Fetch user by username
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'msg': 'invalid credentials'}), 401

    # Include only the role name in JWT claims
    additional_claims = {'role': user.role.name}

    # Create access token
    access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

    # Return token and user info
    return jsonify({
        'access_token': access_token,
        'user': user_schema.dump(user)
    }), 200
