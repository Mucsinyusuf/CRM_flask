from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, mail, ma, cors

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    ma.init_app(app)
    cors.init_app(app)

    # register blueprints
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .customer.routes import customer_bp
    from .support.routes import support_bp
    from .engineer.routes import engineer_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customers')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(engineer_bp, url_prefix='/engineer')

    @app.route('/')
    def index():
        return {'msg': 'Customer Support System API'}

    return app
