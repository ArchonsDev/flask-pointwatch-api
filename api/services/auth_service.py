class AuthService:
    def __init__(self, password_encoder_service, jwt_service):
        self.password_encoder_service = password_encoder_service
        self.jwt_service = jwt_service

    def has_permissions(self, user, minimum_auth=None):
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

        print(user_auth_level >= min_auth_level)
        return user_auth_level >= min_auth_level

    def login(self, user, password):
        # Esnure that the user account is not deleted/disabled.
        if user.is_deleted:
            return None
        # Ensure that the hashed passwords match.
        if not self.password_encoder_service.check_password(user.password, password):
            return None

        return self.jwt_service.generate_token(user.email)
