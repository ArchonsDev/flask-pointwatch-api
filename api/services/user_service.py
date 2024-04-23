from ..services import password_encoder_service, jwt_service

from ..models import db
from ..models.user import User

def create_user(data):
    employee_id = data.get('employee_id')
    email = data.get('email')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    password = data.get('password')

    # Ensure that the Employee ID is present.
    if not employee_id:
        return "Employee ID is required.", 400

    # Ensure that the email is present.
    if not email:
        return "Email is required.", 400
    
    # Ensure that the password is present
    if not password:
        return "Password is required.", 400
    
    # Ensure that the firstname is present.
    if not firstname:
        return "Firstname is required.", 400
    
    # Ensure that the lastname is present.
    if not lastname:
        return "Lastname is required.", 400
    
    existing_user, code = get_user('email', email)

    # Ensure that the email provided is not in use.
    if code == 200 and not existing_user.is_deleted:
        return "Email already in use.", 409

    user = User(
        employee_id=employee_id,
        email=email,
        firstname=firstname,
        lastname=lastname,
        password=password_encoder_service.encode_password(password),
        department=data.get('department') if 'department' in data else None
    )
    
    db.session.add(user)
    db.session.commit()

    return user, 200

def get_user(key, value):
    user = None
    user_query = User.query

    if not hasattr(User, key):
        return f'Cannot retrieve user from given attribute: {key}', 400

    user = user_query.filter(getattr(User, key) == value).first()
    
    # Ensure that the user exists.
    if not user:
        return "User not found.", 404

    return user, 200

def get_all_users(params=None):
    user_query = User.query

    try:
        for key, value in params.items():
            if key == 'is_deleted':
                continue

            if not hasattr(User, key):
                return f'Invalid parameter: {key}', 400

            user_query = user_query.filter(getattr(User, key).like(f'%{value}%'))
            
        return user_query.all(), 200
    except AttributeError:
        return 'One or more query parameters are invalid.', 400

def update_user(id, data):
    user = User.query.get(id)

    # Ensure that the account to be updated exists.
    if not user:
        return "User not found", 404

    if 'employee_id' in data:
        employee_id = data.get('employee_id')
        user, code = get_user('employee_id', employee_id)

        if code == 200:
            return "Employee ID already in use.", 409
        user.employee_id = employee_id
    if 'email' in data:
        email = data.get('email')
        user, code = get_user('email', email)

        if code == 200:
            return "Email already in use.", 409
        user.email = email
    if 'firstname' in data:
        user.firstname = data.get('firstname')
    if 'lastname' in data:
        user.lastname = data.get('lastname')
    if 'password' in data:
        user.password = password_encoder_service.encode_password(data.get('password'))
    if 'department' in data:
        user.department = data.get('department')
    if 'is_staff' in data:
        user.is_staff = data.get('is_staff')
    if 'is_admin' in data:
        user.is_admin = data.get('is_admin')
    if 'is_superuser' in data:
        user.is_suepruser = data.get('is_superuser')
    if 'is_ms_linked' in data:
        user.is_mis_linked = data.get('is_ms_linked')
    if 'is_deleted' in data:
        user.is_deleted = data.get('is_deleted')

    db.session.commit()

    return user.to_dict(), 200
    
def delete_user(id):
    existing_user = User.query.get(id)

    # Ensure that the target account exists.
    if not existing_user:
        return "User not found", 404

    # Ensure that the account is not yet deleted.
    if existing_user.is_deleted:
        return "User already deleted.", 409
    
    existing_user.is_deleted = True

    db.session.commit()
    return {"message": "User deleted."}, 200
