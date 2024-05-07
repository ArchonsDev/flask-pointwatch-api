from flask import Blueprint, request, Response
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import build_response
from ..exceptions import InsufficientPermissionsError, UserNotFoundError, AuthenticationError, ResourceNotFoundError
from ..services import jwt_service, user_service, auth_service, ms_service

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    # Ensure that the requester has permissions.
    if not auth_service.has_permissions(requester, minimum_auth='staff'):
        raise InsufficientPermissionsError("Cannot retrieve user list.")
    
    params = {**request.args}
    users = [user.to_dict() for user in user_service.get_all_users(params=params)]

    return build_response({"users": users}, 200)

@user_bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_user(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user('email', email)
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    
    user = user_service.get_user(id=user_id)
    # Ensure that the target exists.
    if not user:
        raise UserNotFoundError()

    if request.method == 'GET':
        # Ensure that the requester has permission.
        if requester.id != user_id or user.is_deleted and not auth_service.has_permissions(requester, minimum_auth='staff'):
            raise InsufficientPermissionsError("Cannot retrieve user data.")
        
        return build_response(user.to_dict(), 200)
    elif request.method == 'PUT':
        data = request.json
        # Ensure that the requester has the required permission.
        if requester.id != user_id and not auth_service.has_permissions(requester, minimum_auth='staff'):
            raise InsufficientPermissionsError("Cannot update user data.")
        if 'is_staff' in data and not auth_service.has_permissions(requester, minimum_auth='admin'):
            raise InsufficientPermissionsError("Cannot change user staff status.")
        if 'is_admin' in data and not auth_service.has_permissions(requester, minimum_auth='superuser'):
            raise InsufficientPermissionsError("Cannot change user admin status.")
        if 'is_superuser' in data and not auth_service.has_permissions(requester, minimum_auth='superuser'):
            raise InsufficientPermissionsError("Cannot change user superuser status.")
        
        user = user_service.update_user(user, **data)
        return build_response(user.to_dict(), 200)
    elif request.method =='DELETE':
        if requester.id != user_id and not auth_service.has_permissions(requester, minimum_auth='admin'):
            raise InsufficientPermissionsError("Cannot delete user.")

        user_service.delete_user(user)
        return build_response({"message": "User deleted."}, 200)
    
@user_bp.route('/<int:user_id>/points', methods=['GET'])
@jwt_required()
def get_points(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user('email', email)
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    
    user = user_service.get_user(id=user_id)
    # Ensure that the target exists.
    if not user:
        raise UserNotFoundError()

    if request.method == 'GET':
        # Ensure that the requester has permission.
        if requester.id != user_id or user.is_deleted and not auth_service.has_permissions(requester, minimum_auth='staff'):
            raise InsufficientPermissionsError("Cannot retrieve user points.")
        
        params = request.args
        date_fmt = "%m-%d-%Y"
        start_date = None
        end_date = None

        if 'start_date' in params:
            start_date = datetime.strptime(params.get('start_date'), date_fmt).date()

        if 'end_date' in params:
            end_date = datetime.strptime(params.get('end_date'), date_fmt).date()

        points = user_service.get_point_summary(user, start_date=start_date, end_date=end_date)
        
        return build_response(points, 200)

@user_bp.route('/<int:user_id>/avatar', methods=['GET'])
@jwt_required()
def get_avatar(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    # Ensure the requester is authorized.
    if not requester:
        raise AuthenticationError()
    
    user = user_service.get_user(id=user_id)
    # Ensure the target is registered.
    if not user:
        raise UserNotFoundError()
    
    # Ensure that both users have MS Accounts linked.
    if not user.ms_user or not requester.ms_user:
        raise ResourceNotFoundError()
    
    ms_token = requester.ms_user.parse_access_token()
    avatar = ms_service.get_user_avatar(user.email, ms_token)
    # Serve the avatar as an object if it exists.
    if avatar:
        return Response(avatar, mimetype='image/jpg', status=200)
    
    raise ResourceNotFoundError()

@user_bp.route('/<int:user_id>/swtds', methods=['GET'])
@jwt_required()
def get_user_swtds(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    # Ensure the requester is authorized.
    if not requester:
        raise AuthenticationError()
    
    user = user_service.get_user(id=user_id)
    # Ensure the target is registered.
    if not user:
        raise UserNotFoundError()
    
    if request.method == 'GET':
        if requester.id != user.id and not auth_service.has_permissions(requester, minimum_auth='staff'):
            raise InsufficientPermissionsError("Cannot retrieve user SWTDs")
        
        params = request.args
        date_fmt = "%m-%d-%Y"
        start_date = None
        end_date = None

        if 'start_date' in params:
            start_date = datetime.strptime(params.get('start_date'), date_fmt).date()

        if 'end_date' in params:
            end_date = datetime.strptime(params.get('end_date'), date_fmt).date()

        swtd_forms = user_service.get_user_swtd_forms(user, start_date=start_date, end_date=end_date)
        return build_response({"swtd_forms": [form.to_dict() for form in swtd_forms]}, 200)
