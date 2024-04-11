from ..services import password_encoder_service

from ..models import db
from ..models.user import User
from ..models.department import Department

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
        user.password = password_encoder_service.encode_password(data.get('password'))
    if 'department_id' in data:
        department_id = data.get('department_id')

        department = Department.query.get(department_id)

        if not department:
            return "Department not found.", 404
        
        user.department = department

    db.session.commit()
    return {"message": "Account updated."}, 200

def get_user(identity, id):
    requester = User.query.filter_by(email=identity).first()
    existing_user = User.query.get(id)
    
    if not existing_user:
        return "User not found.", 404
    
    if requester.email != existing_user.email and not requester.is_admin:
        return "Unauthorized action.", 401
    
    return existing_user.to_dict(), 200
    
def delete_user(identity, id):
    requester = User.query.filter_by(email=identity).first()

    if not requester.is_admin:
        return "Unauthorized action.", 401

    existing_user = User.query.get(id)

    if existing_user.is_deleted:
        return "User already deleted.", 401
    
    existing_user.is_deleted = True

    db.session.commit()
    return "User deleted.", 200
