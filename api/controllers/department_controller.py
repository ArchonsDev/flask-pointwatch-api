from typing import Any
from datetime import datetime, date

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, department_service, auth_service, ft_service, term_service

from ..exceptions.authorization import AuthorizationError
from ..exceptions.conflct import ResourceAlreadyExistsError
from ..exceptions.resource import ResourceNotFoundError, DepartmentNotFoundError, UserNotFoundError, TermNotFoundError
from ..exceptions.validation import InvalidParameterError, MissingRequiredParameterError

class DepartmentController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.department_service = department_service
        self.auth_service = auth_service
        self.ft_service = ft_service
        self.term_service = term_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('', methods=['GET'])(self.get_all_departments)
        self.route('', methods=['POST'])(self.create_department)
        self.route('/<int:department_id>', methods=['GET'])(self.get_department)
        self.route('/<int:department_id>', methods=['PUT'])(self.update_department)
        self.route('/<int:department_id>', methods=['DELETE'])(self.delete_department)
        self.route('/<int:department_id>/<field_name>', methods=['GET'])(self.get_department_property)
        self.route('/<int:department_id>/export', methods=['GET'])(self.export_department_data)
        self.route('/<int:department_id>/staff/export', methods=['GET'])(self.export_staff_data)

    def get_all_departments(self) -> Response:
        args = {"is_deleted": False, **request.args}
        departments = self.department_service.get_department(lambda q, d: q.filter_by(**args).all())

        return self.build_response({"departments": [d.to_dict() for d in departments]}, 200)

    @jwt_required()
    def create_department(self) -> Response:
        requester = self.jwt_service.get_requester()

        if not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot create department.")
        
        data = {**request.json}
        required_fields = [
            "name",
            "required_points",
            "level",
            "midyear_points",
            "use_schoolyear"
        ]

        self.check_fields(data, required_fields)

        department = self.department_service.create_department(
            name=data.get('name'),
            required_points=data.get('required_points'),
            level=data.get('level').strip().upper(),
            midyear_points=data.get('midyear_points'),
            use_schoolyear=data.get('use_schoolyear')
        )

        return self.build_response({"department": department.to_dict()}, 200)

    def get_department(self, department_id: int) -> Response:
        department = self.department_service.get_department(lambda q, d: q.filter_by(id=department_id, is_deleted=False).first())
        if not department: raise DepartmentNotFoundError()

        return self.build_response({"department": department.to_dict()}, 200)

    @jwt_required()
    def update_department(self, department_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        if not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot update department.")

        department = self.department_service.get_department(lambda q, d: q.filter_by(id=department_id, is_deleted=False).first())
        if not department: raise DepartmentNotFoundError()

        allowed_fields = [
            'is_deleted',
            'name',
            'required_points',
            'midyear_points',
            'use_schoolyear',
            'head_id',
            'level'
        ]
        data = {**request.json}

        if not all(key in allowed_fields for key in data.keys()):
            raise InvalidParameterError()

        if "head_id" in data:
            head_id = data.pop("head_id")

            if head_id == 0:
                head = department.head

                if department.head:
                    if head.access_level < 2:
                        self.user_service.update_user(head, access_level=0)

                data["head"] = None
            else:
                head = self.user_service.get_user(lambda q, u: q.filter_by(id=head_id).first())
                if not head: raise UserNotFoundError()

                if department.head == head: raise ResourceAlreadyExistsError("head")

                if head.access_level < 2:
                    self.user_service.update_user(head, access_level=1)

                data["head"] = head
        
        if "level" in data:
            data["level"] = data.get("level", '').strip().upper()

        department = self.department_service.update_department(department, **data)
        return self.build_response({"department": department.to_dict()}, 200)

    @jwt_required()
    def delete_department(self, department_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        if not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Could not delete department.")

        department = self.department_service.get_department(lambda q, d: q.filter_by(id=department_id, is_deleted=False).first())
        if not department: raise DepartmentNotFoundError()

        self.department_service.delete_department(department)
        return self.build_response({"message": "Department deleted"}, 200)

    @jwt_required()
    def get_department_property(self, department_id: int, field_name: str) -> Response:
        requester = self.jwt_service.get_requester()

        protected_fields = ["members"]

        department = self.department_service.get_department(lambda q, d: q.filter_by(id=department_id, is_deleted=False). first())
        if not department: raise DepartmentNotFoundError()

        if field_name in protected_fields and not department.head == requester and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError(f"Cannot retrieve data for department {field_name}")
        
        if not hasattr(department, field_name): raise ResourceNotFoundError()
        prop = getattr(department, field_name, None)
        use_list = isinstance(prop, list)

        response = {}
        try:
            if use_list:
                prop = list(filter(lambda i: hasattr(i, 'is_deleted') and i.is_deleted == False, prop))

            response[field_name] = [o.to_dict() for o in prop] if use_list else prop.to_dict()
        except AttributeError:
            if isinstance(prop, datetime):
                response[field_name] = prop.strftime("%m-%d-%Y %H:%M")
            elif isinstance(prop, date):
                response[field_name] = prop.strftime("%m-%d-%Y")
            else:
                response[field_name] = prop

        return self.build_response(response, 200)
        
    @jwt_required()
    def export_department_data(self, department_id: int) -> Response:
        requester = self.jwt_service.get_requester()
        
        department = self.department_service.get_department(lambda q, u: q.filter_by(id=department_id, is_deleted=False).first())

        if not department: raise DepartmentNotFoundError()
        
        if not "term_id" in request.args: raise MissingRequiredParameterError("term_id")
        
        term = self.term_service.get_term(lambda q, t: q.filter_by(id=int(request.args.get("term_id", 0)), is_deleted=False).first())
        if not term: raise TermNotFoundError()
        
        if not department.head == requester and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot export staff validation data.")

        content = self.ft_service.export_for_head(requester, department, term)

        headers = {
            'Content-Disposition': f'attachment; filename="{department.name}_Report.pdf"'
        }

        return Response(content, mimetype='application/pdf', status=200, headers=headers)

    @jwt_required()
    def export_staff_data(self, department_id: int) -> Response:
        requester = self.jwt_service.get_requester()
        
        department = self.department_service.get_department(lambda q, u: q.filter_by(id=department_id, is_deleted=False).first())
        if not department: raise DepartmentNotFoundError()
        
        if not "term_id" in request.args: raise MissingRequiredParameterError("term_id")
        
        term = self.term_service.get_term(lambda q, t: q.filter_by(id=int(request.args.get("term_id", 0)), is_deleted=False).first())
        if not term: raise TermNotFoundError()
        
        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot export staff validation data.")

        content = self.ft_service.export_for_staff(requester, department, term)

        headers = {
            'Content-Disposition': f'attachment; filename="{department.name}_Report.pdf"'
        }

        return Response(content, mimetype='application/pdf', status=200, headers=headers)

def setup(app: Flask) -> None:
    app.register_blueprint(DepartmentController('department', __name__, url_prefix='/departments'))
