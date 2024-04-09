from flask import jsonify

from api.models import db
from api.models.user import User

class AuthService:
    @staticmethod
    def create_account(data):
        user = User(
            data['employee_id'],
            data['email'],
            data['firstname'],
            data['lastname'],
            data['password'],
            data['department']
        )

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def login(data):
        pass