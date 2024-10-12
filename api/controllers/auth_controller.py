from typing import Any
import random
import string
from flask import Blueprint, request, url_for, redirect, Response, Flask
from flask_jwt_extended import jwt_required

import redirects
from ..services import auth_service, user_service, jwt_service, password_encoder_service, mail_service
from ..exceptions import DuplicateValueError, UserNotFoundError, AccountUnavailableError, AuthenticationError
from .base_controller import BaseController

class AuthController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)
        
        self.auth_service = auth_service
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
        
        existing_user = self.user_service.get_user(
            lambda q, u: q.filter_by(email=data.get('email')).first()
        )
        # Ensure that the email provided is not in use.
        if existing_user:
            raise DuplicateValueError('email')
        
        existing_user = self.user_service.get_user(
            lambda q, u: q.filter_by(employee_id=data.get('employee_id')).first()
        )
        # Ensure that the employee ID provided is not in use.
        if existing_user:
            raise DuplicateValueError('employee_id')

        user = self.user_service.create_user(**data)

        response = {
            "user": {
                **user.to_dict(),
                "department": user.department.to_dict() if user.department else None,
                "swtd_forms": [s.to_dict() for s in user.swtd_forms],
                "comments": [c.to_dict() for c in user.comments],
                "validated_swtd_forms": [s.to_dict() for s in user.validated_swtd_forms]
            },
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
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(email=data.get('email')).first()
        )
        if not user:
            raise UserNotFoundError()
        
        if user.is_deleted:
            raise AccountUnavailableError()
        
        token = self.auth_service.login(user, data.get('password'))
        # Ensure that the token exists.
        if not token:
            raise AuthenticationError()

        response = {
            "user": {
                **user.to_dict(),
                "department": user.department.to_dict() if user.department else None,
                "swtd_forms": [s.to_dict() for s in user.swtd_forms],
                "comments": [c.to_dict() for c in user.comments],
                "validated_swtd_forms": [s.to_dict() for s in user.validated_swtd_forms]
            },
            "access_token": self.jwt_service.generate_token(user.email)
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
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email, is_deleted=False).first()
        )
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

        user = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        # Ensure that the user exists.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        self.user_service.update_user(user, {"password": data.get('password')})
        return self.build_response({"message": "Password changed."}, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(AuthController('auth', __name__, url_prefix='/auth'))
