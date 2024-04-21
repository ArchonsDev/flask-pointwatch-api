from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import swtd_service, jwt_service

swtd_bp = Blueprint('swtd', __name__, url_prefix='/swtds')

@swtd_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def index():
    identity = jwt_service.get_identity_from_token()
    response = None
    code = 0

    if request.method == 'GET':
        params = request.args
        response, code = swtd_service.get_all_swtds(identity, params)
    elif request.method == 'POST':
        data = request.json
        response, code = swtd_service.create_swtd(identity, data)

    return build_response(response, code)

@swtd_bp.route('/<int:form_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_swtd(form_id):
    identity = jwt_service.get_identity_from_token()
    response = None
    code = 0

    if request.method == 'GET':
        response, code = swtd_service.get_swtd(identity, form_id)
    elif request.method == 'PUT':
        data = request.json
        response, code = swtd_service.update_swtd(identity, form_id, data)
    elif request.method == 'DELETE':
        response, code = swtd_service.delete_swtd(identity, form_id)

    return build_response(response, code)
