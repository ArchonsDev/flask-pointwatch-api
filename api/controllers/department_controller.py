from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from .base_controller import build_response
from ..services import jwt_service, department_service

department_bp = Blueprint('department', __name__)

class DepartmentController:
    @department_bp.route('/', methods=['POST'])
    @jwt_required()
    @staticmethod
    def create_department():
        identity = jwt_service.get_identity_from_token()
        response = None
        code = 0

        if request.method == 'GET':
            response, code = department_service.get_department()
        elif request.method == 'POST':
            data = request.json
            response, code = department_service.create_department(identity, data)
            

        return build_response(response, code)
    
    @department_bp.route('/', methods=['GEt'])
    def get_all_departments():
        response = None
        code = 0

        response, code = department_service.get_all_departments()
        print(response['departments'][0])

        return build_response(response, code)
