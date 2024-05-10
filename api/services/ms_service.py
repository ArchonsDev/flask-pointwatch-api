import json
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from ..models.ms_user import MSUser

class MSService:
    def __init__(self, db, oauth, user_service):
        self.db = db
        self.oauth = oauth
        self.user_service = user_service

    def get_user_data(self, ms_token):
        url = 'https://graph.microsoft.com/v1.0/me'
        user_data = None

        response = self.oauth.microsoft.get(url, token=ms_token)

        if response.status_code == 200:
            user_data = response.json()

        return user_data

    def get_user_avatar(self, email, ms_token):
        url = f'https://graph.microsoft.com/v1.0/users/{email}/photo/$value'

        response = self.oauth.microsoft.get(url.format(email=email), token=ms_token)

        if response.status_code == 200:
            return response.content

        return None

    def create_ms_user(self, id, user_id, access_token):
        ms_user = MSUser(
            id=id,
            user_id=user_id,
            access_token=access_token
        )

        self.db.session.add(ms_user)
        self.db.session.commit()
        
        return ms_user

    def parse_access_token(self, ms_user):
        if not ms_user.access_token:
            return None
        
        return OAuth2Token(json.loads(ms_user.access_token.replace("'", '"')))
