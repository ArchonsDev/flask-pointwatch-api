from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import jwt_service, user_service, auth_service

user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_all_users():
    email = jwt_service.get_identity_from_token()
    requester, code = user_service.get_user('email', email)
    params = request.args
    show_deleted = bool(params.get('is_deleted', False))

    if code == 200 and show_deleted and not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
        return build_response("Insufficient permissions. Cannot retrieve user list.", 403)

    users, code = user_service.get_all_users(params=params)
    
    if code != 200:
        return build_response(users, code)
    
    if show_deleted and auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
        pass
    else:
        users = list(filter(lambda user: user.is_deleted == False, users))

    response = [user.to_dict() for user in users]

    return build_response(response, code)

@user_bp.route('/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_user(user_id):
    email = jwt_service.get_identity_from_token()
    requester, code = user_service.get_user('email', email)

    if request.method == 'GET':
        permissions = ['is_staff', 'is_admin', 'is_superuser']
        user, code = user_service.get_user('email', email)

        if requester.id != user_id or user.is_deleted and not auth_service.has_permissions(requester, permissions):
            return build_response("Insufficient permissions. Cannot retrieve user data.", 403)
        
        response = user.to_dict()
    elif request.method == 'PUT':
        data = request.json

        if requester.id != user_id and not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
            return build_response("Insufficient permissions. Cannot update user data.", 403)
        if 'is_staff' in data and not auth_service.has_permissions(requester, ['is_admin', 'is_superuser']):
            return build_response("Insufficient permissions. Cannot change user staff status.", 403)
        if 'is_admin' in data and not auth_service.has_permissions(requester, ['is_superuser']):
            return build_response("Insufficient permissions. Cannot change user admin status.", 403)
        if 'is_superuser' in data and not auth_service.has_permissions(requester, ['is_superuser']):
            return build_response("Insufficient permissions. Cannot change user superuser status.", 403)
        
        response, code = user_service.update_user(user_id, data)
    elif request.method =='DELETE':
        permissions = ['is_admin', 'is_superuser']

        if requester.id != user_id and not auth_service.has_permissions(requester, permissions):
            return build_response("Insufficient permissions. Cannot delete user.", 403)

        response, code = user_service.delete_user(user_id)

    return build_response(response, code)
