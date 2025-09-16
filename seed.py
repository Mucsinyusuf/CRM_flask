# seed.py
from app import create_app, db
from app.models import Role, User, Ticket, TicketMessage, Audit

def seed_data():
    app = create_app()
    with app.app_context():
        # ===========================
        # Clear existing data
        # ===========================
        db.session.query(Audit).delete()
        db.session.query(TicketMessage).delete()
        db.session.query(Ticket).delete()
        db.session.query(User).delete()
        db.session.query(Role).delete()
        db.session.commit()

        # ===========================
        # ROLES
        # ===========================
        roles = {
            "Admin": Role(name="Admin"),
            "Support Agent": Role(name="Support Agent"),
            "Engineer": Role(name="Engineer"),
            "User": Role(name="User"),
        }
        db.session.add_all(roles.values())
        db.session.commit()

        # ===========================
        # USERS
        # ===========================
        users = [
            User(username="admin", email="admin@example.com", role_id=roles["Admin"].id),
            User(username="support1", email="support1@example.com", role_id=roles["Support Agent"].id),
            User(username="support2", email="support2@example.com", role_id=roles["Support Agent"].id),
            User(username="engineer1", email="engineer1@example.com", role_id=roles["Engineer"].id),
            User(username="engineer2", email="engineer2@example.com", role_id=roles["Engineer"].id),
            User(username="john_doe", email="john@example.com", role_id=roles["User"].id),
            User(username="jane_doe", email="jane@example.com", role_id=roles["User"].id),
        ]

        passwords = ["admin123", "support123", "support123", "engineer123", "engineer123", "user123", "user123"]

        for user, pwd in zip(users, passwords):
            user.set_password(pwd)

        db.session.add_all(users)
        db.session.commit()

        # ===========================
        # TICKETS (assigned to engineers)
        # ===========================
        tickets = [
            Ticket(
                title="Login issue",
                description="I cannot log into my account.",
                status="open",
                created_by=users[5].id,  # john_doe
                assigned_to=users[3].id  # engineer1
            ),
            Ticket(
                title="Payment failed",
                description="My payment did not go through but money was deducted.",
                status="in_progress",
                created_by=users[6].id,  # jane_doe
                assigned_to=users[4].id  # engineer2
            ),
            Ticket(
                title="Feature request",
                description="Please add dark mode to the dashboard.",
                status="closed",
                created_by=users[5].id,  # john_doe
                assigned_to=users[3].id  # engineer1
            ),
        ]
        db.session.add_all(tickets)
        db.session.commit()

        # ===========================
        # TICKET MESSAGES
        # ===========================
        messages = [
            TicketMessage(ticket_id=tickets[0].id, sender_id=users[5].id, message="I tried resetting my password but it still doesn’t work."),
            TicketMessage(ticket_id=tickets[0].id, sender_id=users[3].id, message="We are checking your account, please wait."),
            TicketMessage(ticket_id=tickets[1].id, sender_id=users[6].id, message="The payment deducted from my bank but is not reflected."),
            TicketMessage(ticket_id=tickets[1].id, sender_id=users[4].id, message="We have escalated this to our payments team."),
        ]
        db.session.add_all(messages)
        db.session.commit()

        # ===========================
        # AUDITS
        # ===========================
        audits = [
            Audit(action="Created ticket", user_id=users[5].id, details=f"Ticket '{tickets[0].title}' created."),
            Audit(action="Assigned ticket", user_id=users[3].id, details=f"Ticket '{tickets[0].title}' assigned to engineer1."),
            Audit(action="Created ticket", user_id=users[6].id, details=f"Ticket '{tickets[1].title}' created."),
            Audit(action="Assigned ticket", user_id=users[4].id, details=f"Ticket '{tickets[1].title}' assigned to engineer2."),
            Audit(action="Closed ticket", user_id=users[5].id, details=f"Ticket '{tickets[2].title}' closed."),
        ]
        db.session.add_all(audits)
        db.session.commit()

        print("✅ Database seeded with roles, users, tickets, messages, and audits!")

if __name__ == "__main__":
    seed_data()
