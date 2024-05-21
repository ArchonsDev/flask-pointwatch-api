from typing import Union

from ..models.user import User
from ..services.password_encoder_service import PasswordEncoderService
from ..services.jwt_service import JWTService

class AuthService:
    def __init__(self, password_encoder_service: PasswordEncoderService, jwt_service: JWTService) -> None:
        self.password_encoder_service = password_encoder_service
        self.jwt_service = jwt_service

    def has_permissions(self, user: User, minimum_auth: str=None) -> bool:
        auth_levels = {
            'staff': 1, 
            'admin': 2,
            'superuser': 3
        }

        min_auth_level = auth_levels.get(minimum_auth, 0)
        user_auth_level = 0
        if user.is_staff:
            user_auth_level = 1
        if user.is_admin:
            user_auth_level = 2
        if user.is_superuser:
            user_auth_level = 3

        return user_auth_level >= min_auth_level

    def login(self, user: User, password: str) -> Union[str, None]:
        # Esnure that the user account is not deleted/disabled.
        if user.is_deleted:
            return None
        # Ensure that the hashed passwords match.
        if not self.password_encoder_service.check_password(user.password, password):
            return None

        return self.jwt_service.generate_token(user.email)
