from typing import Any

import random
import string
from flask import Blueprint, request, url_for, redirect, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from .. import oauth
from ..services import auth_service, ms_service, user_service, jwt_service, password_encoder_service, mail_service
from ..exceptions import DuplicateValueError, UserNotFoundError, AccountUnavailableError, AuthenticationError

class AuthController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)
        
        self.auth_service = auth_service
        self.ms_service = ms_service
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.password_encoder_service = password_encoder_service
        self.mail_service = mail_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/register', methods=['POST'])(self.create_account)
        self.route('/login', methods=['POST'])(self.login)
        self.route('/recovery', methods=['POST'])(self.recover_account)
        self.route('/resetpassword', methods=['POST'])(self.reset_password)
        self.route('/microsoft')(self.microsoft)
        self.route('/authorize')(self.authorize)

    def create_account(self) -> Response:
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
        self.check_fields(data, required_fields)
        
        existing_user = self.user_service.get_user(email=data.get('email'))
        # Ensure that the email provided is not in use.
        if existing_user:
            raise DuplicateValueError('email')
        
        existing_user = self.user_service.get_user(employee_id=data.get('employee_id'))
        # Ensure that the employee ID provided is not in use.
        if existing_user:
            raise DuplicateValueError('employee_id')

        user = self.user_service.create_user(
            data.get('employee_id'),
            data.get('email'),
            data.get('firstname'),
            data.get('lastname'),
            data.get('password'),
            department=data.get('department')
        )

        response = {
            "user": user.to_dict(),
            "access_token": self.jwt_service.generate_token(user.email)
        }

        return self.build_response(response, 200)

    def login(self) -> Response:
        data = request.json
        # Define required fields
        required_fields = [
            'email',
            'password',
        ]

        self.check_fields(data, required_fields)

        # Ensure that the user exists.
        user = self.user_service.get_user(email=data.get('email'))
        if not user:
            raise UserNotFoundError()
        
        if user.is_deleted:
            raise AccountUnavailableError()
        
        token = self.auth_service.login(user, data.get('password'))
        # Ensure that the token exists.
        if not token:
            raise AuthenticationError()

        response = {
            "access_token": token,
            "user": user.to_dict()
        }

        return self.build_response(response, 200)

    def recover_account(self) -> Response:
        data = request.json
        # Define required fields
        required_fields = [
            'email',
        ]

        # Ensure required fields are present.
        self.check_fields(data, required_fields)
        # Check if the email is registered to a user.
        user = self.user_service.get_user(email=data.get('email'))
        if user:
            self.mail_service.send_recovery_mail(user.email, user.firstname)

        return self.build_response({"message": "Please check email for instructions on how to reset your password."}, 200)

    @jwt_required()
    def reset_password(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        data = request.json
        # Define required fields
        required_fields = [
            'password',
        ]

        # Ensure that the required fields are present.
        self.check_fields(data, required_fields)

        user = self.user_service.get_user(email=email)
        # Ensure that the user exists.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        self.user_service.update_user(user, password=data.get('password'))
        return self.build_response({"message": "Password changed."}, 200)

    def microsoft(self) -> Response:
        return oauth.microsoft.authorize_redirect(redirect_uri=url_for('auth.authorize', _external=True))

    def authorize(self) -> Response:
        on_fail_redirect_url = 'http://localhost:3000/internalerror' # TODO: Change to actual frontend URL
        on_succ_redirect_url = 'http://localhost:3000/authorized?token={token}&user={user_id}'

        ms_token = oauth.microsoft.authorize_access_token()
        user_data = self.ms_service.get_user_data(ms_token)
        # Ensure that the Microsoft Account Data is present.
        if not user_data:
            return redirect(on_fail_redirect_url)
        
        employee_id = user_data.get('jobTitle')
        email = user_data.get('mail')
        firstname = user_data.get('givenName')
        lastname = user_data.get('surname')
        password = self.password_encoder_service.encode_password(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))

        user = self.user_service.get_user(email=email)
        # Create a local account if not yet registered.
        if not user:
            user = self.user_service.create_user(employee_id, email, firstname, lastname, password)
            # Ensure that a local account has been created.
            if not user:
                return redirect(on_fail_redirect_url)
        
        # Ensure that the user has a linked MS Account
        if not user.ms_user:
            id = user_data.get('id')
            user_id = user.id
            access_token = ms_token

            self.ms_service.create_ms_user(id, user_id, access_token)

        token = self.jwt_service.generate_token(user.email)
        user_id = self.jwt_service.generate_token(user.id)
        return redirect(on_succ_redirect_url.format(token=token, user_id=user_id))

def setup(app: Flask) -> None:
    app.register_blueprint(AuthController('auth', __name__, url_prefix='/auth'))
