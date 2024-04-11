from flask import Blueprint, request, jsonify

from .base_controller import build_response
from ..services import auth_service

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    response = None
    code = 0

    if request.method == 'POST':
        data = request.json
        response, code = auth_service.create_account(data)

    return build_response(response, code)

@auth_bp.route('/login', methods=['POST'])
def login():
    response = None
    code = 0

    if request.method == 'POST':
        data = request.json
        response, code = auth_service.login(data)

    return build_response(response, code)
