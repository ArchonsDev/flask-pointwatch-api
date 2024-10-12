from typing import Any
from datetime import datetime

from flask import Blueprint, request, Response, Flask
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, auth_service, term_service, ft_service, department_service
from ..exceptions import InsufficientPermissionsError, UserNotFoundError, AuthenticationError, ResourceNotFoundError, TermNotFoundError, MissingRequiredPropertyError, DepartmentNotFoundError

class UserController(Blueprint, BaseController):
    def __init__(self, name: str, import_name: str, **kwargs: dict[str, Any]) -> None:
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.auth_service = auth_service
        self.term_service = term_service
        self.ft_service = ft_service
        self.department_service = department_service

        self.map_routes()

    def map_routes(self) -> None:
        self.route('/', methods=['GET'])(self.get_all_users)
        self.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])(self.process_user)
        self.route('/<int:user_id>/points', methods=['GET'])(self.get_points)
        self.route('/<int:user_id>/swtds', methods=['GET'])(self.get_user_swtds)
        self.route('/<int:user_id>/terms/<int:term_id>', methods=['GET', 'POST', 'DELETE'])(self.handle_clearing)
        self.route('/<int:user_id>/swtds/export', methods=['GET'])(self.export_swtd_data)
        self.route('/<int:user_id>/validations/export', methods=['GET'])(self.export_staff_data)
        self.route('/<int:user_id>/clearings/export', methods=['GET'])(self.export_admin_data)

    @jwt_required()
    def get_all_users(self) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        # Ensure that the requester exists.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()

        if request.method == 'GET':
            # URI: GET /users/
            # Description: Retrieves all users, supports params as filters.
            # Required access level: 2 (Head).
            # Params: Refer to user model.

            # Ensure that the requester has permissions.
            if not self.auth_service.has_permissions(requester, minimum_auth='head'):
                raise InsufficientPermissionsError("Cannot retrieve user list.")
            
            # Process Params
            params = {**request.args}
            users = self.user_service.get_user(
                lambda q, u: q.filter_by(is_deleted=False, **params).all()
            )

            response = {
                "users": [{
                    **u.to_dict(),
                    "department": u.department.to_dict() if u.department else None,
                    "swtd_forms": [s.to_dict() for s in u.swtd_forms],
                    "comments": [c.to_dict() for c in u.comments],
                    "validated_swtd_forms": [s.to_dict() for s in u.validated_swtd_forms]
                } for u in users]
            }

            return self.build_response(response, 200)

    @jwt_required()
    def process_user(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )

        # Ensure that the requester exists.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(id=user_id).first()
        )
        # Ensure that the target exists.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()

        if request.method == 'GET':
            # URI: GET /users/<user_id>/
            # Description: Returns a user matching the specified ID.
            # Required access level: 0 (All)-For querying own user data | 2 (Head) for querying other user data.
            # Params: None

            # Ensure that the requester has permission.
            if not self.auth_service.has_permissions(requester, minimum_auth='head') and requester.id != user_id:
                raise InsufficientPermissionsError("Cannot retrieve user data.")
            
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
        elif request.method == 'PUT':
            # URI: PUT /users/<user_id>
            # Description: Updates a user specified by the ID.
            # Required access level: 0 (All)-For own user data | 2 (Head) for other user data.
            # Payload:
            # - password: str
            # - firstname: str
            # - lastname: str
            # - point_balance: float
            # - access_level: int
            # - department_id: int

            data = request.json

            # Ensure that the requester has the required permission.
            if requester.id != user_id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update user data.")
            if 'access_level' in data and not self.auth_service.has_permissions(requester, 'custon', data.get('access_level') + 1):
                raise InsufficientPermissionsError("Cannot update user access level.")
            if 'is_head' in data and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot change user head status.")
            
            if 'department_id' in data:
                department = self.department_service.get_department(
                    lambda q, d: q.filter_by(id=data.get("department_id")).first()
                )

                if not department:
                    print("I was called")
                    raise DepartmentNotFoundError()
            
            user = self.user_service.update_user(user, data)
            return self.build_response(user.to_dict(), 200)
        elif request.method =='DELETE':
            # URI: DEKETE /users/<user_id>
            # Description: Disables the user specified by the ID.
            # Required access level: 0 (All) - For own own account | 2 (Head) - For other users.
            # Params: None

            if requester.id != user_id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete user.")

            self.user_service.delete_user(user)
            return self.build_response({"message": "User deleted."}, 200)
    
    @jwt_required()
    def get_points(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user('email', email)
        # Ensure that the requester exists.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(id=user_id)
        # Ensure that the target exists.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()

        if request.method == 'GET':
            # URI: /GET /users/<user_id>/points
            # Description: Returns the point summary of the user for the specified Term.
            # Required access level: 0 (All) - For own own account | 2 (Head) - For other users.
            # Params:
            # - term_id : ID of Term.

            # Ensure that the requester has permission.
            if requester.id != user_id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user points.")
            
            term_id = int(request.args.get('term_id', 0))

            if not term_id:
                raise MissingRequiredPropertyError('term_id')
            
            term = term_service.get_term(term_id)

            if not term or (term and term.is_deleted):
                raise TermNotFoundError()

            points = self.user_service.get_point_summary(user, term)
            
            return self.build_response(points, 200)

    @jwt_required()
    def get_user_swtds(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)
        # Ensure the requester is authorized.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(id=user_id)
        # Ensure the target is registered.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user SWTDs")
            
            params = request.args
            date_fmt = "%m-%d-%Y"
            start_date = None
            end_date = None

            if 'start_date' in params:
                start_date = datetime.strptime(params.get('start_date'), date_fmt).date()

            if 'end_date' in params:
                end_date = datetime.strptime(params.get('end_date'), date_fmt).date()

            swtd_forms = self.user_service.get_user_swtd_forms(user, start_date=start_date, end_date=end_date)

            if len(swtd_forms) > 0:
                swtd_forms = list(filter(lambda form: form.is_deleted == False, swtd_forms))
            
            return self.build_response({"swtd_forms": [form.to_dict() for form in swtd_forms]}, 200)

    @jwt_required()
    def handle_clearing(self, user_id: int, term_id: int) -> Response:
        email = jwt_service.get_identity_from_token()

        requester = user_service.get_user(email=email)
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = user_service.get_user(id=user_id)
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        term = term_service.get_term(term_id)
        if not term or (term and term.is_deleted):
            raise TermNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot get user term data.")
    
            term_summary = user_service.get_term_summary(user, term)
            return self.build_response(term_summary, 200)

        if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='admin'):
            raise InsufficientPermissionsError("Cannot update user clearance.")
        
        if request.method == 'POST':
            self.user_service.clear_user_for_term(requester, user, term)

            return self.build_response({'message': 'Employee clearance granted for term.'}, 200)
        if request.method == 'DELETE':
            self.user_service.unclear_user_for_term(user, term)

            return self.build_response({'message': 'Employee clearance revoked for term.'}, 200)
        
    @jwt_required()
    def export_swtd_data(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = user_service.get_user(id=user_id)
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot export user SWTD data.")

            content = ft_service.dump_user_swtd_data(requester, user)

            headers = {
                'Content-Disposition': f'attachment; filename="{user.employee_id}_SWTDReport.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)
        
    @jwt_required()
    def export_staff_data(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = user_service.get_user(id=user_id)
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if not self.auth_service.has_permissions(user, minimum_auth='staff'):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='admin'):
                raise InsufficientPermissionsError("Cannot export staff validation data.")

            content = ft_service.dump_staff_validation_data(requester, user)

            headers = {
                'Content-Disposition': f'attachment; filename="{user.employee_id}_ValidationReport.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

    @jwt_required()
    def export_admin_data(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)

        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = user_service.get_user(id=user_id)
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if not self.auth_service.has_permissions(user, minimum_auth='admin'):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='admin'):
                raise InsufficientPermissionsError("Cannot export staff validation data.")

            content = ft_service.dump_admin_clearing_data(requester, user)

            headers = {
                'Content-Disposition': f'attachment; filename="{user.employee_id}_AdminReport.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

def setup(app: Flask) -> None:
    app.register_blueprint(UserController('user', __name__, url_prefix='/users'))
