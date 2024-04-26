import random
import string
from flask import Blueprint, request, url_for, redirect, session
from flask_jwt_extended import jwt_required

from .base_controller import build_response, check_fields
from ..exceptions import DuplicateValueError, UserNotFoundError
from ..services import auth_service, ms_service, oauth, user_service, jwt_service, password_encoder_service, mail_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    # Define required fields
    required_fields = [
        'employee_id',
        'email',
        'firstname',
        'lastname',
        'password'
    ]
    # Ensure the required fields are present.
    check_fields(data, required_fields)
    
    existing_user = user_service.get_user(email=data.get('email'))
    # Ensure that the email provided is not in use.
    if existing_user:
        return DuplicateValueError('email')
    
    existing_user = user_service.get_user(employee_id=data.get('employee_id'))
    # Ensure that the employee ID provided is not in use.
    if existing_user:
        return DuplicateValueError('employee_id')

    user = user_service.create_user(
        data.get('employee_id'),
        data.get('email'),
        data.get('firstname'),
        data.get('lastname'),
        data.get('password'),
        department=data.get('department')
    )

    response = {
        "user": user.to_dict(),
        "access_token": jwt_service.generate_token(user.email)
    }
    
    return build_response(response, 200)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    # Define required fields
    required_fields = [
        'email',
        'password',
    ]

    check_fields(data, required_fields)

    # Ensure that the user exists.
    user = user_service.get_user(email=data.get('email'))
    if not user:
        raise UserNotFoundError()
    
    token = auth_service.login(user, data.get('password'))

    response = {
        "access_token": token,
        "user": user.to_dict()
    }

    return build_response(response, 200)

@auth_bp.route('/recovery', methods=['POST'])
def recover_account():
    data = request.json
    # Define required fields
    required_fields = [
        'email',
    ]

    # Ensure required fields are present.
    check_fields(data, required_fields)
    # Check if the email is registered to a user.
    user = user_service.get_user(email=data.get('email'))
    if user:
        mail_service.send_recovery_mail(user.email, user.firstname)

    return build_response({"message": "Please check email for instructions on how to reset your password."}, 200)

@auth_bp.route('/resetpassword', methods=['POST'])
@jwt_required()
def reset_password():
    email = jwt_service.get_jwt_identity()
    data = request.json
    # Define required fields
    required_fields = [
        'password',
    ]

    # Ensure that the required fields are present.
    check_fields(data, required_fields)

    user = user_service.get_user(email=email)
    # Ensure that the user exists.
    if not user:
        raise UserNotFoundError()
    
    user_service.update_user(user, {'password': data.get('password')})
    return build_response({"message": "Password changed."}, 200)

@auth_bp.route('/microsoft')
def microsoft():
    return oauth.microsoft.authorize_redirect(redirect_uri=url_for('auth.authorize', _external=True))

@auth_bp.route('/authorize')
def authorize():
    session['ms_token'] = oauth.microsoft.authorize_access_token()
    response, code = ms_service.get_user_data()

    # Ensure that the Microsoft Account Data is present.
    if code != 200:
        return redirect(f'http://localhost:3000/internalerror')
    
    data = {
        'employee_id': response.get('jobTitle'),
        'email': response.get('mail'),
        'firstname': response.get('givenName'),
        'lastname': response.get('surname'),
        'password': password_encoder_service.encode_password(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))
    }
    
    user, code = user_service.get_user('email', data.get('email'))

    # Ensuere that a local account exists for the user.
    if code != 200:
        user, code = user_service.create_account(data)

        if code != 200:
            return redirect(f'http://localhost:3000/internalerror')
        
    # Ensure that the user has a linked MS Account
    if not user.is_ms_linked:
        ms_data = {
            'id': response.get('id'),
            'user_id': user.id
        }

        ms_user, code = ms_service.create_ms_user(ms_data)
        
        if code != 200:
            return redirect(f'http://localhost:3000/internalerror')
        
        user_service.update_user(user.id, {'is_ms_linked': True})

    token = jwt_service.generate_token(user.email)
    return redirect(f'http://localhost:3000/authorized?token={token}')
