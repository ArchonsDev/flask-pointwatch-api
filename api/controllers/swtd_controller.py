from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import swtd_service, jwt_service, user_service, auth_service

swtd_bp = Blueprint('swtd', __name__, url_prefix='/swtds')

@swtd_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def index():
    email = jwt_service.get_identity_from_token()
    requester, code = user_service.get_user('email', email)
    params = request.args
    show_deleted = bool(params.get('is_deleted', True))

    if request.method == 'GET':
        params = request.args
        author_id = params.get('author_id')

        if author_id:
            author_id = int(author_id)

        # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
        if (author_id is not None and
            requester.id != author_id and not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser'])
        ) or (
            author_id is None and not auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser'])
        ):
            return {"error": "Insufficient permissions. Cannot retrieve SWTD Forms."}, 403

        swtds, code = swtd_service.get_all_swtds(params=params)

        if code != 200:
            return build_response(swtds, code)
        
        if show_deleted and auth_service.has_permissions(requester, ['is_staff', 'is_admin', 'is_superuser']):
            pass
        else:
            swtds = list(filter(lambda swtd: swtd.is_deleted == False, swtds))

        response = [swtd.to_dict() for swtd in swtds]
    elif request.method == 'POST':
        data = request.json
        swtd, code = swtd_service.create_swtd({"author_id": requester.id, **data})
        response = swtd.to_dict()

    return build_response(response, code)

@swtd_bp.route('/<int:form_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_swtd(form_id):
    email = jwt_service.get_identity_from_token()
    requester, code = user_service.get_user('email', email)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    if request.method == 'GET':
        swtd, code = swtd_service.get_swtd(form_id)

        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            return build_response("Insufficient permissions. Cannot retrieve SWTD form data.", 403)
        
        response = swtd.to_dict()
    elif request.method == 'PUT':
        data = request.json
        swtd, code = swtd_service.update_swtd(form_id, data)

        if swtd.author_id != requester.id and not auth_service.has_permissions(requester, permissions):
            return build_response("Insufficient permissions. Cannot update SWTD form data.", 403)
        
        response = swtd.to_dict()
    elif request.method == 'DELETE':
        swtd, code = swtd_service.get_swtd(form_id)

        if swtd.author_id != requester.id and not auth_service.has_permissions(requester, permissions):
            return build_response("Insufficient permissions. Cannot delete SWTD form.", 403)
        
        response, code = swtd_service.delete_swtd(form_id)

    return build_response(response, code)
