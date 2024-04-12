from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import jwt_service, department_service

department_bp = Blueprint('department', __name__)

@department_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def create_read_departments():
    identity = jwt_service.get_identity_from_token()

    if request.method == 'GET':
        response, code = department_service.get_all_departments()
    elif request.method == 'POST':
        data = request.json
        response, code = department_service.create_department(identity, data)

    return build_response(response, code)

@department_bp.route('/<department_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def process_department(department_id):
    identity = jwt_service.get_identity_from_token()

    if request.method == 'GET':
        response, code = department_service.get_department(department_id)
    elif request.method == 'PUT':
        data = request.json
        response, code = department_service.update_department(identity, department_id, data)
    elif request.method == 'DELETE':
        response, code = department_service.delete_department(identity, department_id)

    return build_response(response, code)
