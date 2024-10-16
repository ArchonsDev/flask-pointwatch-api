from typing import Any

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, department_service, auth_service, ft_service, term_service
from ..exceptions import TermNotFoundError, MissingRequiredPropertyError, InsufficientPermissionsError, DepartmentNotFoundError, AuthenticationError, UserNotFoundError, DuplicateValueError

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
        self.route('/', methods=['GET', 'POST'])(self.index)
        self.route('/<int:department_id>', methods=['GET', 'PUT', 'DELETE'])(self.handle_department)
        self.route('/<int:department_id>/export', methods=['GET'])(self.export_department_data)
        self.route('/<int:department_id>/staff/export', methods=['GET'])(self.export_staff_data)

    @jwt_required()
    def index(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            args = {
                "is_deleted": False,
                **request.args
            }

            use_basic_view = args.pop("basic_view", '').lower() in ("true", "1")

            if not use_basic_view and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Cannot retrieve department list.")

            departments = self.department_service.get_department(
                lambda q, d: q.filter_by(**args).all()
            )

            response = {
                "departments": [{
                    **d.to_dict(),
                    "members": [{
                        **u.to_dict(),
                    "clearances": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.term.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearances))],
                    "clearings": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.user.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, u.comments))],
                    "department": u.department.to_dict() if u.department and u.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.validated_swtd_forms))]
                    } for u in d.members] if not use_basic_view else None,
                    "head": d.head.to_dict() if d.head and not use_basic_view else None
                } for d in departments]
            }

            return self.build_response(response, 200)
        if request.method == 'POST':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot create Department.")

            data = request.json
            required_fields = [
                "name",
                "required_points",
                "level",
                "midyear_points",
                "use_schoolyear"
            ]

            self.check_fields(data, required_fields)

            department = self.department_service.create_department(
                data.get('name'),
                data.get('required_points'),
                data.get('level'),
                data.get('midyear_points'),
                data.get('use_schoolyear')
            )

            response = {
                **department.to_dict()
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
            is_member = requester in department.members
            use_basic_view = request.args.get("basic_view", '') in ("true", "1")

            if not is_member and not use_basic_view and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not retrieve department data.")

            response = {
                **department.to_dict(),
                "members": [{
                    **u.to_dict(),
                    "clearances": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.term.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearances))],
                    "clearings": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.user.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, u.comments))],
                    "department": u.department.to_dict() if u.department and u.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.validated_swtd_forms))]
                } for u in department.members] if requester.is_head and not use_basic_view else None,
                "head": department.head.to_dict() if department.head and not use_basic_view else None
            }
            
            return self.build_response(response, 200)
        if request.method == 'PUT':
            if not requester.is_head and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not update department data.")

            params = {**request.json}

            if "head_id" in params and not "remove_head" in params:
                head_id = params.pop("head_id")

                head = self.user_service.get_user(
                    lambda q, u: q.filter_by(id=head_id).first()
                )

                if not head:
                    raise UserNotFoundError()
                
                if head.is_head:
                    raise DuplicateValueError("head")

                params["head"] = head

            department = self.department_service.update_department(department, **params)

            response = {
                **department.to_dict(),
                "members": [{
                    **u.to_dict(),
                    "clearances": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.term.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearances))],
                    "clearings": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.user.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, u.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, u.comments))],
                    "department": u.department.to_dict() if u.department and u.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.validated_swtd_forms))]
                } for u in department.members] if requester.is_head else None,
                "head": department.head.to_dict() if department.head else None
            }

            return self.build_response(response, 200)
        if request.method == 'DELETE':
            if not self.auth_service.has_permissions(requester, minimum_auth="staff"):
                raise InsufficientPermissionsError("Could not delete department.")

            self.department_service.delete_department(department)
            
            return self.build_response({"message": "Department deleted"}, 200)
        
    @jwt_required()
    def export_department_data(self, department_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        department = self.department_service.get_department(
            lambda q, u: q.filter_by(id=department_id).first()
        )
        if not department or (department and department.is_deleted):
            raise DepartmentNotFoundError()
        
        if not "term_id" in request.args:
            raise MissingRequiredPropertyError("term_id")
        
        term = self.term_service.get_term(
            lambda q, t: q.filter_by(id=int(request.args.get("term_id", 0)), is_deleted=False).first()
        )
        if not term:
            raise TermNotFoundError()
        
        if request.method == 'GET':
            is_head = requester == department.head

            if not is_head and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot export staff validation data.")

            content = self.ft_service.export_for_head(requester, department, term)

            headers = {
                'Content-Disposition': f'attachment; filename="{department.name}_Report.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

    @jwt_required()
    def export_staff_data(self, department_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        department = self.department_service.get_department(
            lambda q, u: q.filter_by(id=department_id).first()
        )
        if not department or (department and department.is_deleted):
            raise DepartmentNotFoundError()
        
        if not "term_id" in request.args:
            raise MissingRequiredPropertyError("term_id")
        
        term = self.term_service.get_term(
            lambda q, t: q.filter_by(id=int(request.args.get("term_id", 0)), is_deleted=False).first()
        )
        if not term:
            raise TermNotFoundError()
        
        if request.method == 'GET':
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot export staff validation data.")

            content = self.ft_service.export_for_staff(requester, department, term)

            headers = {
                'Content-Disposition': f'attachment; filename="{department.name}_Report.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

def setup(app: Flask) -> None:
    app.register_blueprint(DepartmentController('department', __name__, url_prefix='/departments'))
