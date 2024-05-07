from flask import Flask
from flask_cors import CORS

def create_app(testing=False):
    from oauth_config import OAUTH_CONFIG

    app = Flask(__name__)

    if testing:
        app.config.from_object('test_config')
    else:
        app.config.from_object('config')

    from .controllers import blueprints

    for bp in blueprints:
        app.register_blueprint(bp)

    from .services import jwt, mail, oauth
    from .models import db, migrate

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

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

app = create_app()
