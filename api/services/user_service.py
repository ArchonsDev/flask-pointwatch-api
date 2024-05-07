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

    if employee_id:
        return query.filter_by(employee_id=employee_id).first()

    if email:
        return query.filter_by(email=email).first()
    
    user = query.get(id)
    
    if user and user.is_deleted:
        return None

    return user

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

    users = user_query.all()        
    return list(filter(lambda user: user.is_deleted == False, users))

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

def get_user_swtd_forms(user, start_date=None, end_date=None):
    swtd_forms = user.swtd_forms
    swtd_forms = list(filter(lambda form: form.is_deleted == False, swtd_forms))

    if start_date:
        swtd_forms = list(filter(lambda form: form.date >= start_date, swtd_forms))

    if end_date:
        swtd_forms = list(filter(lambda form: form.date <= end_date, swtd_forms))

    return swtd_forms

def get_point_summary(user, start_date=None, end_date=None):
    swtd_forms = user.swtd_forms
    swtd_forms = list(filter(lambda form: form.is_deleted == False, swtd_forms))

    if start_date:
        swtd_forms = list(filter(lambda form: form.date >= start_date, swtd_forms))

    if end_date:
        swtd_forms = list(filter(lambda form: form.date <= end_date, swtd_forms))

    valid_points = 0
    pending_points = 0
    invalid_points = 0

    for form in swtd_forms:
        status = form.validation.status

        if status == 'APPROVED':
            valid_points += form.points
        elif status == 'PENDING':
            pending_points += form.points
        elif status == 'REJECTED':
            invalid_points += form.points

    return {
        "valid_points": valid_points,
        "pending_points": pending_points,
        "invalid_points": invalid_points
    }
