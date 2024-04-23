import random
import string
from flask import Blueprint, request, url_for, redirect

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
    token = oauth.microsoft.authorize_access_token()
    print(token)

    response, code = ms_service.get_user_data(token)
    print(response)

    if not code == 200:
        return build_response(response), code
    
    employee_id, *firstname = response.get('givenName').split(' ')
    data = {
        'employee_id': employee_id,
        'email': response.get('mail'),
        'firstname': ''.join([name + ' ' for name in firstname]).strip(),
        'lastname': response.get('surname'),
        'password': password_encoder_service.encode_password(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))
    }

    response, code = user_service.get_user(data.get('email'), 'email', data.get('email'))

    if code != 200:
        response, code = auth_service.create_account(data)
        if code != 200:
            return build_response({"error": "Could not create account."}, 500)

    response, code = user_service.get_user(data.get('email'), 'email', data.get('email'))
    token = jwt_service.generate_token(data.get('email'))
    user_service.update_user(response.get('email'), response.get('id'), {'ms_token': token})
    return redirect(f'http://localhost:3000/authorized?token={token}')
