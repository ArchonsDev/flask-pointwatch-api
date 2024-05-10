from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import BaseController
from ..services import jwt_service, user_service, auth_service, ms_service
from ..exceptions import InsufficientPermissionsError, UserNotFoundError, AuthenticationError, ResourceNotFoundError

class UserController(Blueprint, BaseController):
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

        self.jwt_service = jwt_service
        self.user_service = user_service
        self.auth_service = auth_service
        self.ms_service = ms_service

        self.map_routes()

    def map_routes(self):
        self.route('/', methods=['GET'])(self.get_all_users)
        self.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])(self.process_user)
        self.route('/<int:user_id>/points', methods=['GET'])(self.get_points)
        self.route('/<int:user_id>/avatar', methods=['GET'])(self.get_avatar)
        self.route('/<int:user_id>/swtds', methods=['GET'])(self.get_user_swtds)

    @jwt_required()
    def get_all_users(self):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)
        # Ensure that the requester exists.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        # Ensure that the requester has permissions.
        if not self.auth_service.has_permissions(requester, minimum_auth='staff'):
            raise InsufficientPermissionsError("Cannot retrieve user list.")
        
        params = {**request.args}
        users = list(filter(lambda user: user.is_deleted == False, users))
        users = [user.to_dict() for user in self.user_service.get_all_users(params=params)]

        return self.build_response({"users": users}, 200)

    @jwt_required()
    def process_user(self, user_id):
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
            # Ensure that the requester has permission.
            if not self.auth_service.has_permissions(requester, minimum_auth='staff') and requester.id != user_id:
                raise InsufficientPermissionsError("Cannot retrieve user data.")
            
            return self.build_response(user.to_dict(), 200)
        elif request.method == 'PUT':
            data = request.json
            # Ensure that the requester has the required permission.
            if requester.id != user_id and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot update user data.")
            if 'is_staff' in data and not self.auth_service.has_permissions(requester, minimum_auth='admin'):
                raise InsufficientPermissionsError("Cannot change user staff status.")
            if 'is_admin' in data and not self.auth_service.has_permissions(requester, minimum_auth='superuser'):
                raise InsufficientPermissionsError("Cannot change user admin status.")
            if 'is_superuser' in data and not self.auth_service.has_permissions(requester, minimum_auth='superuser'):
                raise InsufficientPermissionsError("Cannot change user superuser status.")
            
            user = self.user_service.update_user(user, **data)
            return self.build_response(user.to_dict(), 200)
        elif request.method =='DELETE':
            if requester.id != user_id and not self.auth_service.has_permissions(requester, minimum_auth='admin'):
                raise InsufficientPermissionsError("Cannot delete user.")

            self.user_service.delete_user(user)
            return self.build_response({"message": "User deleted."}, 200)
    
    @jwt_required()
    def get_points(self, user_id):
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
            # Ensure that the requester has permission.
            if requester.id != user_id or user.is_deleted and not self.auth_service.has_permissions(requester, minimum_auth='staff'):
                raise InsufficientPermissionsError("Cannot retrieve user points.")
            
            params = request.args
            date_fmt = "%m-%d-%Y"
            start_date = None
            end_date = None

            if 'start_date' in params:
                start_date = datetime.strptime(params.get('start_date'), date_fmt).date()

            if 'end_date' in params:
                end_date = datetime.strptime(params.get('end_date'), date_fmt).date()

            points = self.user_service.get_point_summary(user, start_date=start_date, end_date=end_date)
            
            return self.build_response(points, 200)

    @jwt_required()
    def get_avatar(self, user_id):
        email = self.jwt_service.get_identity_from_token()
        requester = self.user_service.get_user(email=email)
        # Ensure the requester is authorized.
        if not requester or (requester and requester.is_deleted):
            raise AuthenticationError()
        
        user = self.user_service.get_user(id=user_id)
        # Ensure the target is registered.
        if not user or (user and user.is_deleted):
            raise UserNotFoundError()
        
        # Ensure that both users have MS Accounts linked.
        if not user.ms_user or not requester.ms_user:
            raise ResourceNotFoundError()
        
        ms_token = requester.ms_user.parse_access_token()
        avatar = self.ms_service.get_user_avatar(user.email, ms_token)
        # Serve the avatar as an object if it exists.
        if avatar:
            return Response(avatar, mimetype='image/jpg', status=200)
        
        raise ResourceNotFoundError()

    @jwt_required()
    def get_user_swtds(self, user_id):
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
            swtd_forms = list(filter(lambda form: form.is_deleted == False, swtd_forms))
            return self.build_response({"swtd_forms": [form.to_dict() for form in swtd_forms]}, 200)

def setup(app):
    app.register_blueprint(UserController('user', __name__, url_prefix='/users'))
