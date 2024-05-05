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
    requester = user_service.get_user('email', email)
    params = {**request.args}
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    # Ensure that the requester has permissions.
    if not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
        raise InsufficientPermissionsError("Cannot retrieve user list.")
    
    users = [user.to_dict() for user in user_service.get_all_users(params=params)]
    return build_response({"users": users}, 200)

@user_bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_user(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user('email', email)
    user = user_service.get_user(id=user_id)
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    # Ensure that the target exists.
    if not user:
        raise UserNotFoundError()

    if request.method == 'GET':
        permissions = ['is_staff', 'is_admin', 'is_superuser']
        # Ensure that the requester has permission.
        if requester.id != user_id or user.is_deleted and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve user data.")
        
        return build_response(user.to_dict(), 200)
    elif request.method == 'PUT':
        data = request.json
        # Ensure that the requester has the required permission.
        if requester.id != user_id and not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
            raise InsufficientPermissionsError("Cannot update user data.")
        if 'is_staff' in data and not auth_service.has_permissions(requester, ['is_admin', 'is_superuser']):
            raise InsufficientPermissionsError("Cannot change user staff status.")
        if 'is_admin' in data and not auth_service.has_permissions(requester, ['is_superuser']):
            raise InsufficientPermissionsError("Cannot change user admin status.")
        if 'is_superuser' in data and not auth_service.has_permissions(requester, ['is_superuser']):
            raise InsufficientPermissionsError("Cannot change user superuser status.")
        
        user = user_service.update_user(user, **data)
        return build_response(user.to_dict(), 200)
    elif request.method =='DELETE':
        permissions = ['is_admin', 'is_superuser']

        if requester.id != user_id and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot delete user.")

        user_service.delete_user(user)
        return build_response({"message": "User deleted."}, 200)
    
@user_bp.route('/<int:user_id>/points', methods=['GET'])
@jwt_required()
def get_points(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user('email', email)
    user = user_service.get_user(id=user_id)
    # Ensure that the requester exists.
    if not requester:
        raise AuthenticationError()
    # Ensure that the target exists.
    if not user:
        raise UserNotFoundError()

    if request.method == 'GET':
        permissions = ['is_staff', 'is_admin', 'is_superuser']
        # Ensure that the requester has permission.
        if requester.id != user_id or user.is_deleted and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve user points.")
        
        params = request.args
        date_fmt = "%m-%d-%Y"
        swtd_forms = user.swtd_forms
        swtd_forms = list(filter(lambda swtd_form: swtd_form.is_deleted == False, swtd_forms))

        if 'start_date' in params:
            start_date = datetime.strptime(params.get('start_date'), date_fmt).date()
            swtd_forms = list(filter(lambda swtd_form: swtd_form.date >= start_date, swtd_forms))

        if 'end_date' in params:
            end_date = datetime.strptime(params.get('end_date'), date_fmt).date()
            swtd_forms = list(filter(lambda swtd_form: swtd_form.date <= end_date, swtd_forms))

        points = {
            "valid_points": 0,
            "pending_points": 0,
            "invalid_points": 0
        }

        for swtd_form in swtd_forms:
            status = swtd_form.validation.status

            if status == 'APPROVED':
                points['valid_points'] = points['valid_points'] + swtd_form.points
            elif status == 'PENDING':
                points['pending_points'] = points['pending_points'] + swtd_form.points
            elif status == 'REJECTED':
                points['invalid_points'] = points['invalid_points'] + swtd_form.points
        
        return build_response(points, 200)

@user_bp.route('/<int:user_id>/avatar', methods=['GET'])
@jwt_required()
def get_avatar(user_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    # Ensure the requester is authorized.
    if not requester:
        raise AuthenticationError()
    # Ensure the target is registered.
    user = user_service.get_user(id=user_id)
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
