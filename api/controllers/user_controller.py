from typing import Any

from flask import Blueprint, request, Response, Flask, redirect, url_for
from flask_jwt_extended import jwt_required

from .base_controller import BaseController
from ..services import jwt_service, user_service, auth_service, term_service, ft_service, department_service
from ..exceptions import InsufficientPermissionsError, UserNotFoundError, AuthenticationError, TermNotFoundError, MissingRequiredPropertyError, DepartmentNotFoundError

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
        self.route('/<int:user_id>/department', methods=['GET'])(self.get_user_department)
        self.route('/<int:user_id>/terms/<int:term_id>', methods=['GET', 'POST', 'DELETE'])(self.handle_clearing)
        self.route('/<int:user_id>/swtds/export', methods=['GET'])(self.export_swtd_data)
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
            if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user list.")
            
            # Process Params
            params = {
                "is_deleted": False,
                **request.args
            }

            users = self.user_service.get_user(
                lambda q, u: q.filter_by(**params).all()
            )

            response = {
                "data": [{
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
                    } for c in list(filter(lambda c: c.is_deleted == False,u.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, u.comments))],
                    "department": u.department.to_dict() if u.department and u.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, u.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, u.validated_swtd_forms))]
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
            is_owner = requester == user
            is_head_of_target = requester.department is not None and requester.department == user.department and requester == user.department.head

            # Ensure that the requester has permission.
            if not is_head_of_target and not is_owner and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user data.")
            
            response = {
                "data": {
                    **user.to_dict(),
                    "clearances": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.term.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, user.clearances))],
                    "clearings": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.user.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, user.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, user.comments))],
                    "department": user.department.to_dict() if user.department and user.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, user.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, user.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, user.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, user.validated_swtd_forms))]
                }
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

            is_owner = requester == user

            # Ensure that the requester has the required permission.
            if not is_owner and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update user data.")

            data = request.json

            if 'point_balance' in data and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update user point balance.")

            if 'access_level' in data and not requester.is_staff and not self.auth_service.has_permissions(requester, 'custom', data.get('access_level', 0) + 1):
                raise InsufficientPermissionsError("Cannot update user access level.")
            
            if 'department_id' in data:
                department = self.department_service.get_department(
                    lambda q, d: q.filter_by(id=data.get("department_id")).first()
                )

                if not department:
                    print("I was called")
                    raise DepartmentNotFoundError()
            
            user = self.user_service.update_user(user, data)

            response = {
                "data": {
                    **user.to_dict(),
                    "clearances": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.term.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, user.clearances))],
                    "clearings": [{
                        **c.to_dict(),
                        "user": c.user.to_dict(),
                        "term": c.user.to_dict()
                    } for c in list(filter(lambda c: c.is_deleted == False, user.clearings))],
                    "comments": [c.to_dict() for c in list(filter(lambda c: c.is_deleted == False, user.comments))],
                    "department": user.department.to_dict() if user.department and user.department.is_deleted == False else None,
                    "received_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, user.received_notifications))],
                    "swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, user.swtd_forms))],
                    "triggered_notifications": [n.to_dict() for n in list(filter(lambda n: n.is_deleted == False, user.triggered_notifications))],
                    "validated_swtd_forms": [s.to_dict() for s in list(filter(lambda s: s.is_deleted == False, user.validated_swtd_forms))]
                }
            }

            return self.build_response(response, 200)
        elif request.method =='DELETE':
            # URI: DEKETE /users/<user_id>
            # Description: Disables the user specified by the ID.
            # Required access level: 0 (All) - For own own account | 2 (Head) - For other users.
            # Params: None
            
            is_owner = requester == user

            if not is_owner and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot delete user.")

            self.user_service.delete_user(user)
            return self.build_response({"message": "User deleted."}, 200)
    
    @jwt_required()
    def get_points(self, user_id: int) -> Response:
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
            # URI: /GET /users/<user_id>/points
            # Description: Returns the point summary of the user for the specified Term.
            # Required access level: 0 (All) - For own own account | 2 (Head) - For other users.
            # Params:
            # - term_id : ID of Term.
            is_owner = requester == user
            is_head_of_target = requester.department is not None and requester.department == user.department and requester == user.department.head

            # Ensure that the requester has permission.
            if not is_owner and not is_head_of_target and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user points.")
            
            term_id = int(request.args.get('term_id', 0))

            if not term_id:
                raise MissingRequiredPropertyError('term_id')
            
            term = term_service.get_term(
                lambda q, t: q.filter_by(id=term_id).first()
            )

            if not term or (term and term.is_deleted):
                raise TermNotFoundError()

            points = self.user_service.get_point_summary(user, term)
            
            return self.build_response(points, 200)

    @jwt_required()
    def get_user_swtds(self, user_id: int) -> Response:     
        if request.method == 'GET':
            return redirect(url_for('swtd.index', author_id=user_id, **request.args), code=303)

    @jwt_required()
    def get_user_department(self, user_id: int) -> Response:
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(id=user_id).first()
        )

        if not user or user.is_deleted:
            raise UserNotFoundError()

        if not user.department:
            raise DepartmentNotFoundError()
        
        return redirect(url_for('department.handle_department', department_id=user.department.id), code=303)

    @jwt_required()
    def handle_clearing(self, user_id: int, term_id: int) -> Response:
        email = jwt_service.get_identity_from_token()

        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = user_service.get_user(
            lambda q, u: q.filter_by(id=user_id).first()
        )
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        term = self.term_service.get_term(
            lambda q, t: q.filter_by(id=term_id).first()
        )
        if not term or (term and term.is_deleted):
            raise TermNotFoundError()
        
        if request.method == 'GET':
            is_owner = requester == user

            if not is_owner and not requester.is_head and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot get user term data.")
    
            term_summary = self.user_service.get_term_summary(user, term)
            return self.build_response(term_summary, 200)
        if request.method == 'POST':
            if not requester.is_head and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot grant user clearance.")

            self.user_service.grant_clearance(requester, user, term)

            return redirect(url_for('user.process_user', user_id=user.id), code=303)
        if request.method == 'DELETE':
            if not requester.is_head and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot revoke user clearance.")

            self.user_service.revoke_clearance(user, term)
            
            return redirect(url_for('user.process_user', user_id=user.id), code=303)
        
    @jwt_required()
    def export_swtd_data(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(id=user_id).first()
        )
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='head'):
                raise InsufficientPermissionsError("Cannot export user SWTD data.")

            content = self.ft_service.export_for_employee(requester, user)

            headers = {
                'Content-Disposition': f'attachment; filename="{user.employee_id}_SWTDReport.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

    @jwt_required()
    def export_admin_data(self, user_id: int) -> Response:
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(
            lambda q, u: q.filter_by(email=email).first()
        )
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(
            lambda q, u: q.filter_by(id=user_id).first()
        )
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        if request.method == 'GET':
            if requester.id != user.id and not self.auth_service.has_permissions(requester, minimum_auth='head'):
                raise InsufficientPermissionsError("Cannot export staff validation data.")

            content = ft_service.dump_admin_clearing_data(requester, user)

            headers = {
                'Content-Disposition': f'attachment; filename="{user.employee_id}_AdminReport.pdf"'
            }

            return Response(content, mimetype='application/pdf', status=200, headers=headers)

def setup(app: Flask) -> None:
    app.register_blueprint(UserController('user', __name__, url_prefix='/users'))
