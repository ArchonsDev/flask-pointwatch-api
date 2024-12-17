from typing import Any
from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from ..schemas.user_schema import RegistrationSchema, LoginSchema, AccountRecoverySchema, PasswordResetSchema

from ..services import auth_service, user_service, jwt_service, password_encoder_service, mail_service, department_service

from ..exceptions.authentication import AuthenticationError
from ..exceptions.resource import UserNotFoundError
from ..exceptions.conflct import UserAlreadyExistsError

from .base_controller import BaseController

class AuthController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)
        
        self.auth_service = auth_service
        self.user_service = user_service
        self.jwt_service = jwt_service
        self.password_encoder_service = password_encoder_service
        self.mail_service = mail_service
        self.department_service = department_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/register', methods=['POST'])(self.create_account)
        self.route('/login', methods=['POST'])(self.login)
        self.route('/recovery', methods=['POST'])(self.recover_account)
        self.route('/resetpassword', methods=['POST'])(self.reset_password)

    def create_account(self) -> Response:
        data = self.parse_form(request.json, RegistrationSchema)
        
        existing_user = self.user_service.get_user(lambda q, u: q.filter_by(email=data.get('email')).first())
        if existing_user: raise UserAlreadyExistsError("Email in use.")
        
        existing_user = self.user_service.get_user(lambda q, u: q.filter_by(employee_id=data.get('employee_id')).first())
        if existing_user: raise UserAlreadyExistsError("Employee ID in use.")

        department = self.department_service.get_department(lambda q, d: q.filter_by(id=data.get('department_id', 0), is_deleted=False).first())

        user = self.user_service.create_user(
            employee_id=data.get('employee_id'),
            email=data.get('email'),
            firstname=data.get('firstname'),
            lastname=data.get('lastname'),
            password=self.password_encoder_service.encode_password(data.get('password')),
            department=department
        )

        response = {
            "user": user.to_dict(),
            "access_token": self.jwt_service.generate_token(user.email)
        }

        return self.build_response(response, 200)

    def login(self) -> Response:
        data = self.parse_form(request.json, LoginSchema)

        user = self.user_service.get_user(lambda q, u: q.filter_by(email=data.get('email'), is_deleted=False).first())
        if not user: raise UserNotFoundError()
        
        token = self.auth_service.login(user, data.get('password'))
        if not token: raise AuthenticationError()

        response = {
            "user": user.to_dict(),
            "access_token": token
        }

        return self.build_response(response, 200)

    def recover_account(self) -> Response:
        data = self.parse_form(request.json, AccountRecoverySchema)

        user = self.user_service.get_user(lambda q, u: q.filter_by(email=data.get("email"), is_deleted=False).first())
        if user: self.mail_service.send_recovery_mail(user.email, user.firstname)

        return self.build_response({"message": "Please check email for instructions on how to reset your password."}, 200)

    @jwt_required()
    def reset_password(self) -> Response:
        requester = self.jwt_service.get_requester()

        data = self.parse_form(request.json, PasswordResetSchema)

        password = self.password_encoder_service.encode_password(data.get('password'))

        self.user_service.update_user(requester, password=password)
        return self.build_response({"message": "Password changed."}, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(AuthController('auth', __name__, url_prefix='/auth'))
