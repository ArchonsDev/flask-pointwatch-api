import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from dotenv import load_dotenv

load_dotenv()

jwt = JWTManager()
mail = Mail()
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app(testing=False):
    app = Flask(__name__)

    # Configuration Options
    config = {
        "SECRET_KEY": bytes.fromhex(os.getenv("SECRET_KEY")),
        "SQLALCHEMY_DATABASE_URI": os.getenv("SQLALCHEMY_DATABASE_URI"),
        "SQLALCHEMY_TRACK_MODIFICATIONS": os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS").lower() in ("true", "1"),
        "MAIL_SERVER": os.getenv("MAIL_SERVER"),
        "MAIL_PORT": os.getenv("MAIL_PORT"),
        "MAIL_USE_TLS": os.getenv("MAIL_USE_TLS").lower() in ("true", "1"),
        "MAIL_USERNAME": os.getenv("MAIL_USERNAME"),
        "MAIL_PASSWORD": os.getenv("MAIL_PASSWORD")
    }

    if testing:
        pass
    else:
        app.config.update(config)

    from .controllers import blueprints
    for bp in blueprints:
        bp.setup(app)

    jwt.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(
        app,
        namespaces=[
            '/notifications',
        ],
        cors_allowed_origins=os.getenv("CORS_ALLOWED_ORIGINS")
    )

    with app.app_context():
        if testing:
             db.drop_all()

        db.create_all()
        db.session.commit()

    CORS(
        app,
        resources={
            r"/*": {
                "origins": os.getenv("CORS_ALLOWED_ORIGINS")
            }
        }
    )

    from .exception_handler import handle_exception
    # app.errorhandler(Exception)(handle_exception)
    
    return app
