from flask_jwt_extended import create_access_token, get_jwt_identity, decode_token
from datetime import timedelta, datetime

class JWTService:
    def __init__(self) -> None:
        pass

    def generate_token(self, identity: str) -> str:
        expiry_time = timedelta(hours=1)
        return create_access_token(identity=identity, expires_delta=expiry_time, fresh=True)

    def get_identity_from_token(self) -> str:
        return get_jwt_identity()

    def is_token_valid(self, token: str) -> bool:
        decoded_token = decode_token(token)
        return datetime.now() < datetime.fromtimestamp(decoded_token['exp'])
