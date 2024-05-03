from ..services import password_encoder_service

from ..models import db
from ..models.user import User
from ..exceptions import InvalidParameterError

def create_user(employee_id, email, firstname, lastname, password, department=None):
    user = User(
        employee_id=employee_id,
        email=email,
        firstname=firstname,
        lastname=lastname,
        password=password_encoder_service.encode_password(password),
        department=department
    )
    
    db.session.add(user)
    db.session.commit()

    return user

def get_user(id=None, email=None, employee_id=None):
    query = User.query
    user = None

    if employee_id:
        user = query.filter_by(employee_id=employee_id).first()
        if user: return user

    if email:
        user = query.filter_by(email=email).first()
        if user: return user

    return query.get(id)

def get_all_users(params=None):
    user_query = User.query

    for key, value in params.items():
        # Ensure provided key is valid.
        if not hasattr(User, key):
            raise InvalidParameterError(key)

        if type(key) is str:
            user_query = user_query.filter(getattr(User, key).like(f'%{value}%'))
        else:
            user_query = user_query.filter(getattr(User, key) == value)
        
    return user_query.all()

def update_user(user, **data):
    for key, value in data.items():
        # Ensure provided key is valid.
        if not hasattr(User, key):
            raise InvalidParameterError(key)
        
        if key == 'password':
            value = password_encoder_service.encode_password(value)

        setattr(user, key, value)

    db.session.commit()
    return user
    
def delete_user(user):   
    user.is_deleted = True
    db.session.commit()
