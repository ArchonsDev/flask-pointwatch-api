from flask import Flask
from flask_cors import CORS

from .controllers import blueprints
from .services import jwt, mail
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

    with app.app_context():
        db.create_all()

    CORS(
        app,
        resources={
            r"/": {
                "origins": "*"
            }
        }
    )
    
    return app

app = create_app()
