from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Ensure we have a secret key
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'dev-key-please-change-in-production'

    db.init_app(app)
    login_manager.init_app(app)
    Migrate(app, db)

    with app.app_context():
        # Import models first to ensure they're registered
        from app import models
        
        # Then import and register blueprint
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

        # Create tables
        db.create_all()

    return app 