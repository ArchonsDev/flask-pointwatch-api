from typing import Any
from datetime import datetime, date

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController

from ..services import jwt_service, user_service, auth_service, term_service, ft_service, department_service, password_encoder_service

from ..exceptions.authorization import AuthorizationError
from ..exceptions.resource import ResourceNotFoundError, UserNotFoundError, DepartmentNotFoundError, TermNotFoundError
from ..exceptions.validation import MissingRequiredParameterError, InvalidParameterError

class UserController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.auth_service = auth_service
        self.term_service = term_service
        self.ft_service = ft_service
        self.department_service = department_service
        self.password_encoder_service = password_encoder_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('', methods=['GET'])(self.get_all_users)
        self.route('/<int:user_id>', methods=['GET'])(self.get_user)
        self.route('/<int:user_id>', methods=['PUT'])(self.update_user)
        self.route('/<int:user_id>', methods=['DELETE'])(self.delete_user)
        self.route('/<int:user_id>/<field_name>', methods=['GET'])(self.get_user_property)
        self.route('/<int:user_id>/clearances', methods=['POST'])(self.grant_user_clearance)
        self.route('/<int:user_id>/clearances/<int:clearance_id>', methods=['DELETE'])(self.revoke_user_clearance)
        self.route('/<int:user_id>/points', methods=['GET'])(self.get_user_points)
        self.route('/<int:user_id>/swtds/export', methods=['GET'])(self.export_user_swtd_data)

    @jwt_required()
    def get_all_users(self) -> Response:
        requester = self.jwt_service.get_requester()

        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve user list.")

        params = {"is_deleted": False, **request.args}

        users = self.user_service.get_user(lambda q, u: q.filter_by(**params).all())
        return self.build_response({"users": [u.to_dict() for u in users]}, 200)

    @jwt_required()
    def get_user(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()
        
        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()

        if requester != user and not requester.is_head_of(user) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve user data.")

        return self.build_response({"user": user.to_dict()}, 200)
    
    @jwt_required()
    def update_user(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()

        if requester != user and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot update user data.")

        allowed_fields = [
            'is_deleted',
            'password',
            'employee_id',
            'firstname',
            'lastname',
            'point_balance',
            'is_ms_linked',
            'access_level',
            'department_id'
        ]
        data = {**request.json}
        if not all(key in allowed_fields for key in data.keys()):
            raise InvalidParameterError()
        
        if 'is_deleted' in data and not self.auth_service.has_permissions(minimum_auth="staff"):
            raise AuthorizationError("Cannot update account activation state.")
        
        if 'password' in data:
            data['password'] = self.password_encoder_service.encode_password(data.get('password'))

        if 'point_balance' in data and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot update user point balance.")

        if 'access_level' in data and not requester.is_staff and not self.auth_service.has_permissions(requester, 'custom', data.get('access_level', 0) + 1):
            raise AuthorizationError("Cannot update user access level.")
        
        if 'department_id' in data:
            department_id = data.pop("department_id")
            department = self.department_service.get_department(lambda q, d: q.filter_by(id=department_id, is_deleted=False).first())
            if not department: raise DepartmentNotFoundError()
            data["department"] = department

        user = self.user_service.update_user(user, **data)
        return self.build_response({"user": user.to_dict()}, 200)
    
    @jwt_required()
    def delete_user(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        # Ensure that the target exists.
        if not user: raise UserNotFoundError()

        if requester != user and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot delete user.")

        self.user_service.delete_user(user)
        return self.build_response({"message": "User deleted."}, 200)
    
    @jwt_required()
    def get_user_points(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()
        
        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        # Ensure that the target exists.
        if not user: raise UserNotFoundError()

        if request.method == 'GET':
            # Ensure that the requester has permission.
            if requester != user and not requester.is_head_of(user) and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise AuthorizationError("Cannot retrieve user points.")
            
            term_id = int(request.args.get('term_id', 0))
            if not term_id: raise MissingRequiredParameterError('term_id')
            
            term = self.term_service.get_term(lambda q, t: q.filter_by(id=term_id, is_deleted=False).first())
            if not term: raise TermNotFoundError()

            points = self.user_service.get_point_summary(user, term)
            return self.build_response({"points": points}, 200)

    @jwt_required()
    def export_user_swtd_data(self, user_id: int) -> Response:
        requester = jwt_service.get_requester()
        
        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()
        
        if requester != user and not self.auth_service.has_permissions(requester, minimum_auth='head'):
            raise AuthorizationError("Cannot export user SWTD data.")

        content = self.ft_service.export_for_employee(requester, user)

        headers = {
            'Content-Disposition': f'attachment; filename="{user.employee_id}_SWTDReport.pdf"'
        }

        return Response(content, mimetype='application/pdf', status=200, headers=headers)
        
    @jwt_required()
    def get_user_property(self, user_id: int, field_name: str) -> Response:
        requester = self.jwt_service.get_requester()
        
        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()

        # Ensure that the requester has permission.
        if not requester.is_head_of(user) and requester != user and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise AuthorizationError("Cannot retrieve user data.")
        
        if not hasattr(user, field_name): raise ResourceNotFoundError()

        prop = getattr(user, field_name, None)

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
    def grant_user_clearance(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        data = {**request.json}

        if "term_id" not in data: raise MissingRequiredParameterError("term_id")

        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=data.get("term_id"), is_deleted=False).first())
        if not term: raise TermNotFoundError()

        if not requester.is_head_of(user) and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot grant user clearance")
        
        clearance = self.user_service.grant_clearance(requester, user, term)

        return self.build_response({"clearance": clearance.to_dict()}, 200)
    
    @jwt_required()
    def revoke_user_clearance(self, user_id: int) -> Response:
        requester = self.jwt_service.get_requester()

        params = {**request.args}

        if "term_id" not in params: raise MissingRequiredParameterError("term_id")

        user = self.user_service.get_user(lambda q, u: q.filter_by(id=user_id, is_deleted=False).first())
        if not user: raise UserNotFoundError()

        term = self.term_service.get_term(lambda q, t: q.filter_by(id=int(params.get("term_id", 0)), is_deleted=False).first())
        if not term: raise TermNotFoundError()

        if not requester.is_head_of(user) and not self.auth_service.has_permissions(requester, minimum_auth="staff"):
            raise AuthorizationError("Cannot revoke user clearance.")
        
        self.user_service.revoke_clearance(user, term)

        return self.build_response({"message": "Clearance revoked."}, 200)

def setup(app: Flask) -> None:
    app.register_blueprint(UserController('user', __name__, url_prefix='/users'))
