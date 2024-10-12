from typing import Any
from datetime import datetime

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, department_service, auth_service
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, MissingRequiredPropertyError, DepartmentNotFoundError, AuthenticationError

class DepartmentController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.department_service = department_service
        self.auth_service = auth_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/', methods=['GET', 'POST'])(self.index)
        self.route('/<int:department_id>', methods=['GET', 'PUT', 'DELETE'])(self.handle_department)

    @jwt_required()
    def index(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            if not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Cannot retrieve department list.")

            departments = self.department_service.get_department(
                lambda q, d: q.filter_by(**request.args, is_deleted=False).all()
            )

            return self.build_response({"departments": [d.to_dict() for d in departments]}, 200)
        if request.method == 'POST':
            data = request.json
            required_fields = [
                "name",
                "required_points",
                "classification",
                "midyear_points"
            ]

            self.check_fields(data, required_fields)

            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot create Department.")
            
            department = self.department_service.create_department(
                data.get('name'),
                data.get('required_points'),
                data.get('classification'),
                data.get('midyear_points')
            )

            response = {
                **department.to_dict(),
                "members": [u.to_dict() for u in department.members],
                "head": department.head.to_dict() if department.head else None
            }

            return self.build_response(response, 200)
    
    @jwt_required()
    def handle_department(self, department_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        department = self.department_service.get_department(
            lambda q, d: q.filter_by(id=department_id).first()
        )
        if not department or (department and department.is_deleted):
            raise DepartmentNotFoundError()

        if request.method == 'GET':
            if not requester.is_head and not requester in department.members and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not retrieve department data.")

            response = {
                **department.to_dict(),
                "members": [u.to_dict() for u in department.members],
                "head": department.head.to_dict() if department.head else None
            }
            
            return self.build_response(response, 200)
        if request.method == 'PUT':
            if not requester.is_head and not requester in department.members and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not retrieve department data.")

            department = self.department_service.update_department(department, **request.json)

            response = {
                **department.to_dict(),
                "members": [u.to_dict() for u in department.members],
                "head": department.head.to_dict() if department.head else None
            }

            return self.build_response(response, 200)
        if request.method == 'DELETE':
            if not requester.is_head and not requester in department.members and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not retrieve department data.")

            self.department_service.delete_department(department)
            
            return self.build_response({"message": "Department deleted"}, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(DepartmentController('department', __name__, url_prefix='/departments'))
