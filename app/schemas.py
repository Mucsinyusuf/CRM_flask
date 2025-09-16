# app/schemas.py
from .extensions import ma
from .models import User, Role, Ticket, TicketMessage
from marshmallow import fields


class RoleSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Role
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()


class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True

    id = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    role_id = ma.auto_field()
    created_at = ma.auto_field()

    # Nested role info (optional but useful)
    role = fields.Nested(RoleSchema, only=("id", "name"))


class TicketMessageSchema(ma.SQLAlchemySchema):
    class Meta:
        model = TicketMessage
        load_instance = True
        include_fk = True

    id = ma.auto_field()
    ticket_id = ma.auto_field()
    sender_id = ma.auto_field()
    message = ma.auto_field()
    created_at = ma.auto_field()

    # Nested sender info
    sender = fields.Nested(UserSchema, only=("id", "username", "email"))


class TicketSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Ticket
        load_instance = True
        include_fk = True

    id = ma.auto_field()
    title = ma.auto_field()
    description = ma.auto_field()
    status = ma.auto_field()
    created_by = ma.auto_field()
    assigned_to = ma.auto_field()
    created_at = ma.auto_field()
    updated_at = ma.auto_field()

    # Nested creator & assignee
    creator = fields.Nested(UserSchema, only=("id", "username", "email"))
    assignee = fields.Nested(UserSchema, only=("id", "username", "email"))

    # Include related messages
    messages = fields.List(fields.Nested(TicketMessageSchema))
