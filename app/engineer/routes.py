from flask import Blueprint, jsonify
from ..models import Ticket, Audit
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..schemas import TicketSchema
from ..middleware.decorators import role_required

# Blueprint
engineer_bp = Blueprint("engineer", __name__)

# Schemas
ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# ============================
# List tickets assigned to engineer
# ============================
@engineer_bp.route("/my-assigned", methods=["GET"])
@jwt_required()
@role_required("Engineer")
def my_assigned():
    """List all tickets assigned to the logged-in engineer."""
    user_id = int(get_jwt_identity())
    tickets = (
        Ticket.query.filter_by(assigned_to=user_id)
        .order_by(Ticket.created_at.desc())
        .all()
    )
    return jsonify(tickets_schema.dump(tickets)), 200


# ============================
# Resolve a ticket
# ============================
@engineer_bp.route("/tickets/<int:ticket_id>/resolve", methods=["POST"])
@jwt_required()
@role_required("Engineer")
def resolve_ticket(ticket_id):
    """Resolve a ticket assigned to the logged-in engineer."""
    user_id = int(get_jwt_identity())
    ticket = Ticket.query.get_or_404(ticket_id)

    if ticket.assigned_to != user_id:
        return jsonify({"msg": "Forbidden - ticket not assigned to you"}), 403

    if ticket.status == "resolved":
        return jsonify({"msg": "Ticket is already resolved"}), 400

    ticket.status = "resolved"
    db.session.add(ticket)

    # Add audit log
    audit = Audit(
        action="resolve",
        user_id=user_id,
        details=f"Ticket {ticket.id} resolved by engineer {user_id}"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify(ticket_schema.dump(ticket)), 200
