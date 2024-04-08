from flask import Blueprint, request
from app.models import NewUser
from app.models import LoginForm
from app.services import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

class AuthController:
    @staticmethod
    @auth_bp.route('/register', methods=['POST'])
    def register():
        if request.method == 'POST':
            payload = request.json

            user_data = NewUser(
                payload.get('employee_id'),
                payload.get('email'),
                payload.get('firstname'),
                payload.get('lastname'),
                payload.get('password'),
                payload.get('department')
            )

            response = AuthService.create_account(user_data)

    @staticmethod
    @auth_bp.route('/login', methods=['POST'])
    def login():
        if request.method == 'POST':
            payload = request.json

            user_data = LoginForm(
                payload.get('username'),
                payload.get('lastname')
            )

            response = AuthService.login(user_data)
            