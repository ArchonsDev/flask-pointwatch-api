from flask import Flask
from flask_cors import CORS

from oauth_config import OAUTH_CONFIG

from .exception_handler import handle_exception
from .controllers import blueprints
from .services import jwt, mail, oauth
from .models import db, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    for bp in blueprints:
        app.register_blueprint(bp)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    with app.app_context():
        db.create_all()

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

    app.errorhandler(Exception)(handle_exception)
    
    return app

app = create_app()
