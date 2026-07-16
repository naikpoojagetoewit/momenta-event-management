import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, mail, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['INVOICE_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.client.routes import client_bp
    from app.admin.routes import admin_bp
    from app.manager.routes import manager_bp
    from app.team.routes import team_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(team_bp, url_prefix='/team')

    @app.context_processor
    def inject_globals():
        return {'site_name': 'Momenta', 'tagline': 'Creating Moments That Matter'}

    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    return app
