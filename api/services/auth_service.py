from ..models import db
from ..models.user import User

from .password_encoder_service import PasswordEncoderService
from .jwt_service import JWTService

class AuthService:
    @staticmethod
    def create_account(data):
        employee_id = data.get('employee_id')
        email = data.get('email')
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        password = PasswordEncoderService.encode_password(data.get('password'))
        department = data.get('department')

        if not email or not password:
            return "Email and password are required.", 400
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and not existing_user.is_deleted:
            return "Email already in use", 409

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

        return user.to_dict(), 200

    @staticmethod
    def login(data):
        email = data.get('email')
        password = data.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            return "User not found.", 404
        
        if existing_user.is_deleted:
            return "This account is disabled.", 403
        
        if not PasswordEncoderService.check_password(existing_user.password, password):
            return "Invalid credentials.", 401

        return JWTService.generate_token(email), 200
