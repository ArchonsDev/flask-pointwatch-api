from ..services import password_encoder_service

from ..models import db
from ..models.user import User

def get_all_users(identity):
    requester = User.query.filter_by(email=identity).first()

    # TODO: Ensure that the requester is an HRD staff or HRD admin.
    if not requester.is_staff or not requester.is_admin:
        return {"error": "Insufficient permissions. Cannot retrieve user list."}, 403

    users = User.query.filter_by(is_deleted=False).all()
    return {"users": [user.to_dict() for user in users]}, 200

def get_user(identity, user_id):
    requester = User.query.filter_by(email=identity).first()
    existing_user = User.query.get(user_id)
    
    # Ensure that the user exists.
    if not existing_user:
        return {"error": "User not found."}, 404
    
    # Ensure that the requester is the account owner or is an HRD admin.
    if requester.email != existing_user.email and not requester.is_admin:
        return {"error": "Insufficient permissions. Cannot retrieve user data."}, 403
    
    return existing_user.to_dict(), 200

def update_user(identity, user_id, data):
    requester = User.query.filter_by(email=identity).first()
    user = User.query.get(user_id)

    # Ensure that the account to be updated exists.
    if not user:
        return {"error": "User not found"}, 404
    
    # Ensure that the requester is the account owner or is an HRD admin.
    if requester.email != user.email and not user.is_admin:
        return {"error": "Insufficient permissions. Cannot update target user data."}, 403

    if 'firstname' in data:
        user.firstname = data.get('firstname')
    if 'lastname' in data:
        user.lastname = data.get('lastname')
    if 'password' in data:
        user.password = password_encoder_service.encode_password(data.get('password'))
    if 'department' in data:
        user.department = data.get('department')
    if 'is_staff' in data:
        if not requester.is_admin:
            return {"error": "Inusfficient permissions. Cannot promote target user to staff."}, 403
        
        user.is_admin = data.get('is_admin')

    db.session.commit()
    return {"message": "Account updated."}, 200
    
def delete_user(identity, user_id):
    requester = User.query.filter_by(email=identity).first()

    # Ensure that the requester is an HRD admin.
    if not requester.is_admin:
        return {"error": "Insufficient permissions. Cannot delete or disable target user."}, 403

    existing_user = User.query.get(user_id)

    # Ensure that the target account exists.
    if not existing_user:
        return {"error": "User not found"}, 404

    # Ensure that the account is not yet deleted.
    if existing_user.is_deleted:
        return {"error": "User already deleted."}, 409
    
    existing_user.is_deleted = True

    db.session.commit()
    return {"message": "User deleted."}, 200
