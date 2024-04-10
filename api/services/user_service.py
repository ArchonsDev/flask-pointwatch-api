from ..services.password_encoder_service import PasswordEncoderService

from ..models import db
from ..models.user import User

class UserService:
    @staticmethod
    def update_user(identity, id, data):
        requester = User.query.filter_by(email=identity).first()

        if not requester:
            return "Unauthorized action.", 401
        
        user = User.query.get(id)

        if not user:
            return "User not found", 404
        
        if requester.email != user.email and not user.is_admin:
            return "Unauthorized action", 401
        
        if 'firstname' in data:
            user.firstname = data.get('firstname')
        if 'lastname' in data:
            user.lastname = data.get('lastname')
        if 'password' in data:
            user.password = PasswordEncoderService.encode_password(data.get('password'))
        if 'department' in data:
            user.department = data.get('department')

        db.session.commit()
        return user.to_dict(), 200
    
    @staticmethod
    def get_user(identity, id):
        requester = User.query.filter_by(email=identity).first()
        existing_user = User.query.get(id)
        
        if not existing_user:
            return "User not found.", 404
        
        if requester.email != existing_user.email and not requester.is_admin:
            return "Unauthorized action.", 401
        
        return existing_user.to_dict(), 200
