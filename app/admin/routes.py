from flask import Blueprint, jsonify, request
from ..models import Ticket, User
from ..extensions import db
from ..middleware.decorators import role_required
from ..schemas import UserSchema, TicketSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

admin_bp = Blueprint("admin", __name__)

# Schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# ============================
# USER CRUD
# ============================
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@role_required("Admin")
def list_users():
    users = User.query.all()
    return jsonify({"users": users_schema.dump(users)}), 200


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@role_required("Admin")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"user": user_schema.dump(user)}), 200


@admin_bp.route("/users", methods=["POST"])
@jwt_required()
@role_required("Admin")
def create_user():
    data = request.get_json() or {}
    required_fields = ["username", "email", "password", "role_id"]

    if not all(field in data for field in required_fields):
        return jsonify({"msg": "username, email, password, and role_id are required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already exists"}), 400

    new_user = User(
        username=data["username"],
        email=data["email"],
        role_id=data["role_id"]
    )
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User created", "user": user_schema.dump(new_user)}), 201


@admin_bp.route("/users/<int:user_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required("Admin")
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    if "username" in data:
        user.username = data["username"]
    if "email" in data:
        user.email = data["email"]
    if "role_id" in data:
        user.role_id = data["role_id"]
    if "password" in data:
        user.set_password(data["password"])

    db.session.commit()
    return jsonify({"msg": "User updated", "user": user_schema.dump(user)}), 200


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@role_required("Admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": f"User '{user.username}' deleted"}), 200


# ============================
# TICKET CRUD
# ============================
@admin_bp.route("/tickets", methods=["GET"])
@jwt_required()
@role_required("Admin")
def list_all_tickets():
    tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    return jsonify({"tickets": tickets_schema.dump(tickets)}), 200


@admin_bp.route("/tickets/<int:ticket_id>", methods=["GET"])
@jwt_required()
@role_required("Admin")
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify({"ticket": ticket_schema.dump(ticket)}), 200


@admin_bp.route("/tickets", methods=["POST"])
@jwt_required()
@role_required("Admin")
def create_ticket_admin():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"msg": "title is required"}), 400

    creator_id = data.get("creator_id") or int(get_jwt_identity())
    assigned_to = data.get("assigned_to")

    # Validate assigned_to exists
    if assigned_to and not User.query.get(assigned_to):
        return jsonify({"msg": "assigned_to user not found"}), 404

    ticket = Ticket(
        title=title,
        description=data.get("description", ""),
        status=data.get("status", "open"),
        created_by=creator_id,
        assigned_to=assigned_to,
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify({"msg": "Ticket created", "ticket": ticket_schema.dump(ticket)}), 201


@admin_bp.route("/tickets/<int:ticket_id>", methods=["PUT", "PATCH"])
@jwt_required()
@role_required("Admin")
def update_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json() or {}

    if "title" in data:
        ticket.title = data["title"]
    if "description" in data:
        ticket.description = data["description"]
    if "status" in data:
        ticket.status = data["status"]
    if "assigned_to" in data:
        assigned_to = data["assigned_to"]
        if assigned_to and not User.query.get(assigned_to):
            return jsonify({"msg": "assigned_to user not found"}), 404
        ticket.assigned_to = assigned_to

    db.session.commit()
    return jsonify({"msg": "Ticket updated", "ticket": ticket_schema.dump(ticket)}), 200


@admin_bp.route("/tickets/<int:ticket_id>", methods=["DELETE"])
@jwt_required()
@role_required("Admin")
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"msg": f"Ticket '{ticket.title}' deleted"}), 200
