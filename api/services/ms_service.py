from flask import session
from sqlalchemy.exc import IntegrityError

from . import oauth, user_service

from ..models import db
from ..models.ms_user import MSUser

def requires_ms_token(func):
    def wrapper(*args, **kwrgs):
        if not session.get('ms_token'):
            return "Access token is missing.", 403
        
        return func(*args, **kwrgs)
    return wrapper

@requires_ms_token
def get_user_data():  
    response = oauth.microsoft.get('https://graph.microsoft.com/v1.0/me', token=session.get('ms_token'))

    if not response.status_code == 200:
        return {'error': "Failed to retrieve user data."}, 500
    
    user_info = response.json()

    return user_info, 200

@requires_ms_token
def get_user_avatar(email):
    response = oauth.microsoft.get(f'https://graph.microsoft.com/v1.0/users/{email}/photo/$value', token=session.get('ms_token'))
    return response.json(), response.status

@requires_ms_token
def create_ms_user(data):
    ms_user = MSUser(
        id=data.get('id'),
        user_id=data.get('user_id')
    )

    db.session.add(ms_user)

    try:
        db.session.commit()
    except IntegrityError:
        return "Failed to link microsoft user account.", 409
    
    return ms_user, 200