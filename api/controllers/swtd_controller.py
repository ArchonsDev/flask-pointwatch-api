import os

from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime

from .base_controller import build_response, check_fields
from ..exceptions import InsufficientPermissionsError, InvalidDateTimeFormat, SWTDFormNotFoundError, MissingRequiredPropertyError
from ..services import swtd_service, jwt_service, user_service, auth_service, ft_service, swtd_validation_service, swtd_comment_service

swtd_bp = Blueprint('swtd', __name__, url_prefix='/swtds')

@swtd_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def index():
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)

    if request.method == 'GET':
        permissions = ['is_staff', 'is_admin', 'is_superuser']
        params = {"is_deleted": False, **request.args}
        author_id = int(params.get('author_id', 0))
        # Ensure that a non-staff/admin/superuser requester can only request SWTD Forms they are the author of.
        if requester.id != author_id and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD Forms.")
        
        swtds = [swtd.to_dict() for swtd in swtd_service.get_all_swtds(params=params)]
        return build_response({"swtds": swtds}, 200)
    elif request.method == 'POST':
        data = request.form
        required_fields = [
            'author_id',
            'title',
            'category',
            'venue',
            'role',
            'date',
            'time_started',
            'time_finished',
            'points',
            'benefits',
        ]

        check_fields(data, required_fields)

        if len(request.files) != 1:
            raise MissingRequiredPropertyError("proof")

        try:
            data = {
                **data,
                'date': datetime.strptime(data.get('date'), '%m-%d-%Y').date(),
                'time_started': datetime.strptime(data.get('time_started'), '%H:%M').time(),
                'time_finished': datetime.strptime(data.get('time_finished'), '%H:%M').time()
            }
        except Exception:
            raise InvalidDateTimeFormat()
        
        swtd = swtd_service.create_swtd(
            data.get('author_id'),
            data.get('title'),
            data.get('venue'),
            data.get('category'),
            data.get('role'),
            data.get('date'),
            data.get('time_started'),
            data.get('time_finished'),
            data.get('points'),
            data.get('benefits')
        )

        file = request.files.get('proof')

        swtd_validation_service.create_validation(swtd, file.filename)
        ft_service.save(requester.id, swtd.id, file)

        return build_response(swtd.to_dict(), 200)

@swtd_bp.route('/<int:form_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_swtd(form_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    swtd = swtd_service.get_swtd(form_id)
    if not swtd:
        raise SWTDFormNotFoundError()

    if request.method == 'GET':
        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")
        
        return build_response(swtd.to_dict(), 200)
    elif request.method == 'PUT':
        data = request.json

        try:
            data = {
                **data,
                'date': datetime.strptime(data.get('date'), '%m-%d-%Y').date(),
                'time_started': datetime.strptime(data.get('time_started'), '%H:%M').time(),
                'time_finished': datetime.strptime(data.get('time_finished'), '%H:%M').time()
            }
        except Exception:
            raise InvalidDateTimeFormat()

        if swtd.author_id != requester.id and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot update SWTD form data.")
        
        swtd = swtd_service.update_swtd(swtd, **data)
        swtd_validation_service.update_validation(swtd, requester, valid="PENDING")
        return build_response(swtd.to_dict(), 200)
    elif request.method == 'DELETE':
        if swtd.author_id != requester.id and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot delete SWTD form.")
        
        swtd_service.delete_swtd(swtd)
        return build_response({"message": "SWTD Form deleted."}, 200)
    
@swtd_bp.route('/<int:form_id>/comments')
@jwt_required()
def process_comments(form_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    swtd = swtd_service.get_swtd(form_id)
    if not swtd:
        raise SWTDFormNotFoundError()

    if request.method == 'GET':
        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form comments.")
        
        return build_response({"comments": [comment.to_dict() for comment in swtd.comments]}, 200)
    if request.method == 'POST':
        data = request.json
        required_fields = ['message']

        check_fields(data, required_fields)

        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form comments.")
        
        swtd_comment_service.create_comment(swtd, requester, data.get('message'))
        return build_response({"comments": [comment.to_dict() for comment in swtd.comments]}, 200)
    
@swtd_bp.route('/<int:form_id>/comments/<int:comment_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_swtd(form_id, comment_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    swtd = swtd_service.get_swtd(form_id)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    if not swtd:
        raise SWTDFormNotFoundError()
    
    comment = filter(lambda comment: comment.id == comment_id, swtd.comments)

    if not comment:
        # TODO: Create custom exception.
        pass
    
    if request.method == 'GET':
        if (comment.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form comment.")
        
        return build_response(comment.to_dict(), 200)
    if request.method == 'PUT':
        data = request.json
        required_fields = ['message']

        check_fields(data, required_fields)

        swtd_comment_service.update_comment(comment, data.get('message'))
        return build_response(comment.to_dict(), 200)
    if request.method == 'DELETE':
        if (comment.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form comment.")
        
        swtd_comment_service.delete_comment(comment)
        return build_response({"message": "Comment deleted."}, 200)
    
@swtd_bp.route('/<int:form_id>/validation', methods=["GET", "PUT"])
@jwt_required()
def process_validation(form_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    swtd = swtd_service.get_swtd(form_id)
    if not swtd:
        raise SWTDFormNotFoundError()

    if request.method == 'GET':
        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")
        
        return build_response(swtd.validation.to_dict(), 200)
    if request.method == 'PUT':
        if not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form data.")

        data = request.json
        if not 'status' in data:
            raise MissingRequiredPropertyError('status')
        
        if data.get('status') == 'APPROVED':
            swtd_validation_service.update_validation(swtd, requester, valid=True)
        elif data.get('status') == 'REJECTED':
            swtd_validation_service.update_validation(swtd, requester, valid=False)
        else:
            raise MissingRequiredPropertyError('status')

        return build_response(swtd.validation.to_dict(), 200) # TODO: Verify this is updated.

@swtd_bp.route('/<int:form_id>/validation/proof', methods=['GET', 'PUT'])
@jwt_required()
def show_proof(form_id):
    email = jwt_service.get_identity_from_token()
    requester = user_service.get_user(email=email)
    permissions = [
        'is_staff',
        'is_admin',
        'is_superuser'
    ]

    swtd = swtd_service.get_swtd(form_id)
    if not swtd:
        raise SWTDFormNotFoundError()

    if request.method == 'GET':
        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot retrieve SWTD form proof.")

        fp = os.path.join(ft_service.data_dir, str(swtd.author.id), str(swtd.id), swtd.validation.proof)
        return send_file(fp)
    if request.method == 'PUT':
        if (swtd.author_id != requester.id or swtd.is_deleted) and not auth_service.has_permissions(requester, permissions):
            raise InsufficientPermissionsError("Cannot update SWTD form proof.")
        
        if len(request.files) != 1:
            raise MissingRequiredPropertyError("proof")
        
        file = request.files.get('proof')

        swtd_validation_service.update_proof(swtd, file)
        ft_service.save(requester.id, swtd.id, file)

        return build_response(swtd.to_dict(), 200)
    