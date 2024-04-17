from flask_jwt_extended import JWTManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth

jwt = JWTManager()
mail = Mail()
oauth = OAuth()
