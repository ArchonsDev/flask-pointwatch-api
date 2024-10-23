from datetime import timedelta

from flask_jwt_extended import create_access_token, get_jwt_identity

from ..models.user import User

from ..exceptions.authentication import AuthenticationError

class JWTService:
    def __init__(self) -> None:
        pass

    def generate_token(self, identity: str) -> str:
        return create_access_token(identity=identity, expires_delta=timedelta(hours=1), fresh=True)

    def get_requester(self) -> str:
        user = User.query.filter_by(email=get_jwt_identity(), is_deleted=False).first()
        if not user: raise AuthenticationError()

        return user
