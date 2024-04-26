from flask import session
from sqlalchemy.exc import IntegrityError

from . import oauth, user_service

from ..models import db
from ..models.ms_user import MSUser

def get_user_data(ms_token):
    url = 'https://graph.microsoft.com/v1.0/me'
    user_data = None

    response = oauth.microsoft.get(url, token=ms_token)

    if response.status_code == 200:
        user_data = response.json()

    return user_data

def get_user_avatar(email, ms_token):
    url = f'https://graph.microsoft.com/v1.0/users/{email}/photo/$value'

    response = oauth.microsoft.get(url.format(email=email), token=ms_token)

    if response.status_code == 200:
        return response.content

    return None

def create_ms_user(id, user_id, access_token):
    ms_user = MSUser(
        id=id,
        user_id=user_id,
        access_token=access_token
    )

    db.session.add(ms_user)
    db.session.commit()
    
    return ms_user
