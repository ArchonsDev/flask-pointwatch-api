from flask_jwt_extended import create_access_token, get_jwt_identity, decode_token
from datetime import timedelta, datetime

def generate_token(identity):
    expiry_time = timedelta(hours=1)
    return create_access_token(identity=identity, expires_delta=expiry_time, fresh=True)

def get_identity_from_token():
    return get_jwt_identity()

def is_token_valid(token):
    decoded_token = decode_token(token)
    return datetime.now() < datetime.fromtimestamp(decoded_token['exp'])