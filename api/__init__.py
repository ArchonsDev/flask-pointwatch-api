from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from os import urandom

from .controllers.auth_controller import auth_bp
from .controllers.user_controller import user_bp
from .controllers.department_controller import department_bp

from .models import db

def create_app():
    app = Flask(__name__)
    app.secret_key = urandom(32)
    app.config.from_object('config')

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix="/users")
    app.register_blueprint(department_bp, url_prefix='/departments')

    db.init_app(app)

    jwt = JWTManager(app)

    return app

app = create_app()
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
