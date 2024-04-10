from flask import jsonify

from api.models import db
from api.models.user import User
from .password_encoder_service import PasswordEncoderService
from .jwt_service import JWTService

class AuthService:
    @staticmethod
    def create_account(request):
        data = request.json

        employee_id = data.get('employee_id')
        email = data.get('email')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        password = PasswordEncoderService.encode_password(data.get('password'))
        department = data.get('department')

        if not email or not password:
            return jsonify({'error': 'Email and password are required.'}), 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'Email already in use.'}), 409

        user = User(
            employee_id=employee_id,
            email=email,
            firstname=firstname,
            lastname=lastname,
            password=password,
            department=department
        )
        
        db.session.add(user)
        db.session.commit()

        return jsonify(user.to_dict()), 200

    @staticmethod
    def login(request):
        data = request.json

        email = data.get('email')
        password = data.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            return jsonify({'error': 'User not found.'}), 404
        
        if not PasswordEncoderService.check_password(existing_user.password, password):
            return jsonify({'error': 'Invalid credentials.'}), 401

        access_token = JWTService.generate_token(email)
        return jsonify({'access_token': access_token}), 200
