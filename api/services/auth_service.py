from flask import current_app

from ..models import db
from ..models.user import User

from . import password_encoder_service, jwt_service, mail_service, user_service

def has_permissions(user, permissions=[]):
    flag = False

    for key in permissions:
        if not hasattr(User, key):
            continue

        if getattr(user, key) == True:
            flag = True

    return flag

def login(data):
    email = data.get('email')
    password = data.get('password')

    existing_user, code = user_service.get_user('email', email)

    # Ensure that the user exists.
    if code == 404:
        return "User not found.", 404
    
    # Esnure that the user account is not deleted/disabled.
    if code == 200 and existing_user.is_deleted:
        return "This account has been disabled.", 403
    
    # Ensure that the credentials are valid.
    if not password_encoder_service.check_password(existing_user.password, password):
        return "Invalid credentials.", 401
    
    response = {
        "user": existing_user.to_dict(),
        "access_token": jwt_service.generate_token(existing_user.email)
    }

    return response, 200

def recover_account(data):
    email = data.get('email')
    existing_user, code = user_service.get_user('email', email)
    
    if code == 200 and not existing_user.is_deleted:
        token = jwt_service.generate_token(existing_user.email)
        with current_app.open_resource('templates/account_recovery_instructions_template.txt', 'r') as f:
            mail_template = f.read()

        mail_body = mail_template.format(username=existing_user.firstname, token=token)
        mail_service.send_mail('Account Recovery | PointWatch', [existing_user.email,], mail_body)

    response = {
        "message": "Account recovery instructions sent to email (if registered)."
    }
    
    return response, 200

def reset_password(token, password):
    email = jwt_service.decode_token(token).get('sub')
    user, code = user_service.get_user('email', email)

    if code == 200:
        user.password = password_encoder_service.encode_password(password)
        db.session.commit()

    response = {
        "message": "Password changed."
    }

    return response, 200
