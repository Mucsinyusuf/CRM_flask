#!/bin/bash
echo "Create admin user (edit credentials as needed)"
python - <<'PY'
from app import create_app
from app.extensions import db
from app.models import User
app = create_app(); app.app_context().push()
if not User.query.filter_by(username='admin').first():
    u = User(username='admin', email='admin@example.com', role='admin')
    u.set_password('adminpass')
    db.session.add(u); db.session.commit()
    print('admin created')
else:
    print('admin exists')
PY
