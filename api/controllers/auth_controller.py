import random
import string
from flask import Blueprint, request, url_for, redirect, session

from .base_controller import build_response
from ..services import auth_service, ms_service, oauth, user_service, jwt_service, password_encoder_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    user, code = user_service.create_user(data)

    response = {
        "user": user.to_dict(),
        "access_token": jwt_service.generate_token(user.email)
    }
    
    return build_response(response, code)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    response, code = auth_service.login(data)

    return build_response(response, code)

@auth_bp.route('/recovery', methods=['POST'])
def recover_account():
    data = request.json
    response, code = auth_service.recover_account(data)

    return build_response(response, code)

@auth_bp.route('/resetpassword', methods=['POST'])
def reset_password():
    token = request.args.get('token')
    data = request.json
    
    response, code = auth_service.reset_password(token, data.get('password'))

    return build_response(response, code)

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
