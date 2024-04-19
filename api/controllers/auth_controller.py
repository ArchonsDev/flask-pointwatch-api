import random
import string
from flask import Blueprint, request, url_for

from .base_controller import build_response
from ..services import auth_service, oauth, oauth_service, user_service, jwt_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    response, code = auth_service.create_account(data)
    
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
    
    response, code = auth_service.reset_password(token, data)

    return build_response(response, code)

@auth_bp.route('/microsoft')
def microsoft():
    return oauth.microsoft.authorize_redirect(redirect_uri=url_for('auth.authorize', _external=True))

@auth_bp.route('/authorize')
def authorize():
    token = oauth.microsoft.authorize_access_token()

    response, code = oauth_service.get_user_data(token)

    if not code == 200:
        return build_response(response), code
    
    email = response.get('mail')
    employee_id, *firstname = response.get('givenName').split(' ')
    print(employee_id, firstname)
    lastname = response.get('surname')
    password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))

    data = {
        'employee_id': employee_id,
        'email': email,
        'firstname': ''.join([name + ' ' for name in firstname]).strip(),
        'lastname': lastname,
        'password': password
    }

    response, code = user_service.get_user(identity=data.get('email'))

    if not code == 200:
        response, code = auth_service.create_account(data)

        if code == 200:
            return build_response({"access_token": jwt_service.generate_token(data.get('email'))}, 200)
        else:
            return build_response({"error": "Could not create account."}, 500)
    else:
        return build_response({"access_token": jwt_service.generate_token(data.get('email'))}, 200)
