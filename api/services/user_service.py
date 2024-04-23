from ..services import password_encoder_service

from ..models import db
from ..models.user import User

def get_user(identity, key, value):
    requester = User.query.filter_by(email=identity).first()
    
    existing_user = None
    user_query = User.query

    if not hasattr(User, key):
        return {'error': f'Cannot retrieve user from given attribute: {key}'}, 400

    existing_user = user_query.filter(getattr(User, key) == value).first()
    
    # Ensure that the user exists.
    if not existing_user:
        return {"error": "User not found."}, 404
    
    # Ensure that the requester is the account owner or is an HRD admin.
    if requester.email != existing_user.email and not (requester.is_admin or requester.is_staff):
        return {"error": "Insufficient permissions. Cannot retrieve user data."}, 403
    
    return existing_user.to_dict(), 200

def get_all_users(identity, params=None):
    requester = User.query.filter_by(email=identity).first()

    # Ensure that the requester is an HRD staff or HRD admin.
    if not requester.is_staff and not requester.is_admin:
        return {"error": "Insufficient permissions. Cannot retrieve user list."}, 403
    
    user_query = User.query
    
    if not params:
        users = user_query.filter_by(is_deleted=False).all()
    else:
        try:
            for key, value in params.items():
                if not hasattr(User, key):
                    return {'error': f'Invalid parameter: {key}'}, 400

                user_query = user_query.filter(getattr(User, key).like(f'%{value}%'))
                
            users = user_query.all()
        except AttributeError:
            return {'error': 'One or more query parameters are invalid.'}, 400
        
    return {"users": [user.to_dict() for user in users]}, 200

def update_user(identity, id, data):
    requester = User.query.filter_by(email=identity).first()
    user = User.query.get(id)

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
            return {"error": "Inusfficient permissions. Cannot modify user staff permissions."}, 403
        
        user.is_admin = data.get('is_admin')
    if 'is_admin' in data:
        if not requester.is_superuser:
            return {"error": "Inusfficient permissions. Cannot modify user admin permissions"}, 403 
        
        user.is_superuser = data.get('is_superuser')
    if 'is_deleted' in data:
        if not requester.is_admin:
            return {"error": "Inusfficient permissions. Cannot change account deletion status."}, 403
        
        user.is_deleted = data.get('is_deleted')

    if 'ms_token' in data:
        user.ms_token = data.get('ms_token')

    db.session.commit()
    return {"message": "Account updated."}, 200
    
def delete_user(identity, id):
    requester = User.query.filter_by(email=identity).first()

    # Ensure that the requester is an HRD admin.
    if not requester.is_admin:
        return {"error": "Insufficient permissions. Cannot delete or disable target user."}, 403

    existing_user = User.query.get(id)

    # Ensure that the target account exists.
    if not existing_user:
        return {"error": "User not found"}, 404

    # Ensure that the account is not yet deleted.
    if existing_user.is_deleted:
        return {"error": "User already deleted."}, 409
    
    existing_user.is_deleted = True

    db.session.commit()
    return {"message": "User deleted."}, 200
