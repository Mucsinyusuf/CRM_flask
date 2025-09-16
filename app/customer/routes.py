from flask import Blueprint, request, jsonify
from ..models import Ticket
from ..extensions import db
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from ..schemas import TicketSchema

customer_bp = Blueprint("customer", __name__)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)


# ============================
# CREATE TICKET
# ============================
@customer_bp.route("/tickets", methods=["POST"])
@jwt_required()
def create_ticket():
    """Allow customers and admins to create tickets."""
    claims = get_jwt()
    role = claims.get("role")
    
    if role not in ("User", "Admin"):  # match role names in your seed
        return jsonify({"msg": "Forbidden - only customers or admins can create tickets"}), 403

    data = request.get_json() or {}
    title = data.get("title")
    description = data.get("description", "")
    status = data.get("status", "open")

    if not title:
        return jsonify({"msg": "title required"}), 400

    creator_id = int(get_jwt_identity())
    ticket = Ticket(
        title=title,
        description=description,
        status=status,
        created_by=creator_id,
        assigned_to=data.get("assigned_to"),
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 201


# ============================
# LIST TICKETS
# ============================
@customer_bp.route("/tickets", methods=["GET"])
@jwt_required()
def list_tickets():
    """List tickets visible to the logged-in user based on role."""
    claims = get_jwt()
    role = claims.get("role")
    user_id = int(get_jwt_identity())

    if role == "Admin":
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
    elif role == "Engineer":
        tickets = (
            Ticket.query.filter_by(assigned_to=user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )
    else:  # User -> only tickets they created
        tickets = (
            Ticket.query.filter_by(created_by=user_id)
            .order_by(Ticket.created_at.desc())
            .all()
        )

    return jsonify(tickets_schema.dump(tickets)), 200
