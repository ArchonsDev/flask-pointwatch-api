import json
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from . import db

class MSUser(db.Model):
    __tablename__ = 'tblmsusers'

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tblusers.id'), nullable=False, unique=True)
    access_token = db.Column(db.TEXT, nullable=True)

    def parse_access_token(self):
        token_data = json.loads(self.access_token.replace("'", '"')) if self.access_token else None
        
        if token_data:
            return OAuth2Token(token_data)
        
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id
        }
