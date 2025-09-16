# Customer Support System - Flask scaffold

This is an advanced scaffold for a role-based customer support system:
- JWT auth
- Roles: admin, customer, support, engineer
- SQLAlchemy models (User, Issue, Audit)
- Flask-Migrate ready migrations
- Email (Flask-Mail) and SMS (Twilio optional)
- Marshmallow schemas for validation/serialization
- Role-based decorators
- Example endpoints for each role

## How to use

1. Copy `.env.example` -> `.env` and fill credentials.
2. Create venv and install requirements:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Initialize DB migrations:
   ```
   export FLASK_APP=manage.py
   flask db init
   flask db migrate -m "initial"
   flask db upgrade
   ```
4. Create admin user:
   ```
   python -c "from app import create_app; from app.extensions import db; from app.models import User
   app=create_app(); app.app_context().push();
   u=User(username='admin', email='admin@example.com', role='admin'); u.set_password('adminpass');
   db.session.add(u); db.session.commit(); print('created', u.id)"
   ```
5. Run:
   ```
   python manage.py
   ```
# CRM_flask
