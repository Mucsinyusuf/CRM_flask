from flask import Blueprint, jsonify, request
from ..models import Ticket, User, Audit
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..middleware.decorators import role_required
from ..schemas import TicketSchema
from ..services.email import send_email
from ..services.sms import send_sms

support_bp = Blueprint("support", __name__)
ticket_schema = TicketSchema()


# ============================
# List all open tickets
# ============================
@support_bp.route("/open", methods=["GET"])
@jwt_required()
@role_required("Admin", "Support Agent")
def open_tickets():
    """List all open tickets visible to admins and support staff."""
    tickets = Ticket.query.filter_by(status="open").order_by(Ticket.created_at.desc()).all()
    return jsonify(ticket_schema.dump(tickets, many=True)), 200


# ============================
# Assign ticket to engineer
# ============================
@support_bp.route("/assign/<int:ticket_id>", methods=["POST"])
@jwt_required()
@role_required("Admin")
def assign_ticket(ticket_id):
    """Assign a ticket to an engineer. Only admins can perform this action."""
    data = request.get_json() or {}
    assignee_id = data.get("assignee_id")

    if not assignee_id:
        return jsonify({"msg": "assignee_id is required"}), 400

    ticket = Ticket.query.get_or_404(ticket_id)
    assignee = User.query.get(int(assignee_id))

    # Validate assignee is an Engineer
    if not assignee or assignee.role.name != "Engineer":
        return jsonify({"msg": "assignee must be an Engineer"}), 400

    ticket.assigned_to = assignee.id
    ticket.status = "in_progress"
    db.session.add(ticket)

    # Add audit log
    audit = Audit(
        action="assign",
        user_id=int(get_jwt_identity()),
        details=f"Ticket {ticket.id} assigned to user {assignee.id}",
    )
    db.session.add(audit)
    db.session.commit()

    # Notify assignee (best-effort)
    if assignee.email:
        send_email(
            assignee.email,
            "Ticket Assigned",
            f"You have been assigned ticket: {ticket.title}",
        )
    send_sms(None, f"You have been assigned ticket: {ticket.title}")

    return jsonify(ticket_schema.dump(ticket)), 200


# ============================
# Resolve ticket
# ============================
@support_bp.route("/resolve/<int:ticket_id>", methods=["POST"])
@jwt_required()
@role_required("Engineer")
def resolve_ticket(ticket_id):
    """Mark a ticket as resolved. Only engineers can perform this action."""
    ticket = Ticket.query.get_or_404(ticket_id)

    # Only assigned engineer can resolve
    current_user_id = int(get_jwt_identity())
    if ticket.assigned_to != current_user_id:
        return jsonify({"msg": "Only the assigned engineer can resolve this ticket"}), 403

    ticket.status = "resolved"
    db.session.add(ticket)

    # Audit log
    audit = Audit(
        action="resolve",
        user_id=current_user_id,
        details=f"Ticket {ticket.id} marked as resolved",
    )
    db.session.add(audit)
    db.session.commit()

    # Notify creator + admin + support
    recipients = set()
    if ticket.created_by:
        creator = User.query.get(ticket.created_by)
        if creator and creator.email:
            recipients.add(creator.email)

    # Notify all admins and support agents
    staff_users = User.query.join(User.role).filter(User.role.has(name="Admin") | User.role.has(name="Support Agent")).all()
    for u in staff_users:
        if u.email:
            recipients.add(u.email)

    for email in recipients:
        send_email(
            email,
            f"Ticket Resolved: {ticket.title}",
            f"The ticket '{ticket.title}' has been resolved by {User.query.get(current_user_id).username}."
        )

    return jsonify(ticket_schema.dump(ticket)), 200
