from typing import Union

from ..models.user import User
from ..services.password_encoder_service import PasswordEncoderService
from ..services.jwt_service import JWTService

class AuthService:
    def __init__(self, password_encoder_service: PasswordEncoderService, jwt_service: JWTService) -> None:
        self.password_encoder_service = password_encoder_service
        self.jwt_service = jwt_service

    def has_permissions(self, user: User, minimum_auth: str, min_access_level: int=0) -> bool:
        auth_levels = {
            "head": 1,
            "staff": 2,
            "superuser": 3
        }

        return user.access_level >= auth_levels.get(minimum_auth, min_access_level)

    def login(self, user: User, password: str) -> Union[str, None]:
        if user.is_deleted or not self.password_encoder_service.check_password(user.password, password):
            return None

        return self.jwt_service.generate_token(user.email)
