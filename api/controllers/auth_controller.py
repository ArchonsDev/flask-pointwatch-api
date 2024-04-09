from flask import Blueprint, request

from api.services import AuthService
from api.models.user import User

auth_bp = Blueprint('auth', __name__)

class AuthController:
    @staticmethod
    @auth_bp.route('/register', methods=['POST'])
    def register():
        if request.method == 'POST':
            response = AuthService.create_account(request.form)

    @staticmethod
    @auth_bp.route('/login', methods=['POST'])
    def login():
        if request.method == 'POST':
            user = User(
                request.form['email'],
                request.form['password'],
            )

            response = AuthService.login(user)
