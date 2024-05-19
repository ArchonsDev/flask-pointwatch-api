from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO

jwt = JWTManager()
mail = Mail()
oauth = OAuth()
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

def create_app(testing=False):
    from oauth_config import OAUTH_CONFIG

    app = Flask(__name__)
    if testing:
        app.config.from_object('test_config')
    else:
        app.config.from_object('config')

    from .controllers import blueprints
    for bp in blueprints:
        bp.setup(app)

    jwt.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(
        app,
        namespaces=[
            '/notifications',
        ]
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
                "origins": "*"
            }
        }
    )

    for provider, config in OAUTH_CONFIG.items():
         oauth.register(
            name=provider,
            **config
        )

    from .exception_handler import handle_exception
    app.errorhandler(Exception)(handle_exception)
    
    return app
