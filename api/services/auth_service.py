from flask import current_app

from ..models import db
from ..models.user import User

from . import password_encoder_service, jwt_service, mail_service

def create_account(data):
    employee_id = data.get('employee_id')
    email = data.get('email')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    password = password_encoder_service.encode_password(data.get('password'))
    department = data.get('department')

    # Ensure that the Employee ID is present.
    if not employee_id:
        return {"error": "Employee ID is required."}, 400

    # Ensure that the email and password fields are present.
    if not email or not password:
        return {"error": "Email and password are required."}, 400
    
    # Ensure that the firstname and lastname fields are present.
    if not firstname and not lastname:
        return "Firstname and Lastname are required.", 400
    
    # Ensure that the department field is present.
    if not department:
        return "Department is required.", 400
    
    # Ensure that the email provided is not in use.
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and not existing_user.is_deleted:
        return {"error": "Email already in use."}, 409

    user = User(
        employee_id=employee_id,
        email=email,
        firstname=firstname,
        lastname=lastname,
        password=password,
        department=department
    )
    
    db.session.add(user)
    db.session.commit()

    return {'message': "Account created."}, 200

def login(data):
    email = data.get('email')
    password = data.get('password')

    existing_user = User.query.filter_by(email=email).first()

    # Ensure that the user exists.
    if not existing_user:
        return {"error": "User not found."}, 404
    
    # Esnure that the user account is not deleted/disabled.
    if existing_user.is_deleted:
        return {"error": "This account has been disabled."}, 403
    
    # Ensure that the credentials are valid.
    if not password_encoder_service.check_password(existing_user.password, password):
        return {"error": "Invalid credentials."}, 401

    return {'access_token': jwt_service.generate_token(email)}, 200

def recover_account(data):
    email = data.get('email')

    existing_user = User.query.filter_by(email=email).first()
    # Ensure that the email is registered to an account.
    if not existing_user:
        return {"error": "Email is not registered."}, 404
    
    token = jwt_service.generate_token(existing_user.email)
    # TODO: Mail token to the registered email
    with current_app.open_resource('templates/account_recovery_instructions_template.txt', 'r') as f:
        mail_template = f.read()

    mail_body = mail_template.format(username=existing_user.firstname, token=token)
    mail_service.send_mail('Account Recovery | PointWatch', [existing_user.email,], mail_body)
    
    return {'message': 'Account recovery instructions sent.'}, 200

def reset_password(token, data):
    if not token:
        return {"error": "Access token is required."}, 400
    
    if not 'password' in data:
        return {"error": "New password is required."}, 400
    
    identity = jwt_service.decode_token(token).get('sub')
    user = User.query.filter_by(email=identity).first()

    user.password = password_encoder_service.encode_password(data.get('password'))
    
    db.session.commit()
    return {'message': "Password changed."}, 200
