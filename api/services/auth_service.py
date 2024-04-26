from . import password_encoder_service, jwt_service
from ..models.user import User

def has_permissions(user, permissions=[]):
    flag = False

    for key in permissions:
        if not hasattr(User, key):
            continue

        if getattr(user, key) == True:
            flag = True

    return flag

def login(user, password):
    # Esnure that the user account is not deleted/disabled.
    if user.is_deleted:
        return None
    # Ensure that the hashed passwords match.
    if not password_encoder_service.check_password(user.password, password):
        return None

    return jwt_service.generate_token(user.email)
