from typing import Any, Union
import json

from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

from ..models.ms_user import MSUser
from ..services.user_service import UserService

class MSService:
    def __init__(self, db: SQLAlchemy, oauth: OAuth, user_service: UserService) -> None:
        self.db = db
        self.oauth = oauth
        self.user_service = user_service

    def get_user_data(self, ms_token: dict[str, Any]) -> dict[str, Any]:
        url = 'https://graph.microsoft.com/v1.0/me'
        user_data = None

        response = self.oauth.microsoft.get(url, token=ms_token)

        if response.status_code == 200:
            user_data = response.json()

        return user_data

    def get_user_avatar(self, email: str, ms_token: dict[Any]) -> Union[dict[str, Any], None]:
        url = f'https://graph.microsoft.com/v1.0/users/{email}/photo/$value'

        response = self.oauth.microsoft.get(url.format(email=email), token=ms_token)

        if response.status_code == 200:
            return response.content

        return None

    def create_ms_user(self, id: int, user_id: int, access_token: str) -> MSUser:
        ms_user = MSUser(
            id=id,
            user_id=user_id,
            access_token=access_token
        )

        self.db.session.add(ms_user)
        self.db.session.commit()
        
        return ms_user

    def parse_access_token(self, ms_user: MSUser) -> OAuth2Token:
        if not ms_user.access_token:
            return None
        
        return OAuth2Token(json.loads(ms_user.access_token.replace("'", '"')))
