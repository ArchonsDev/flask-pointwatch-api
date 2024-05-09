import random
import string
from unittest import TestCase

from api import db, create_app
from api.models.user import User
from api.services import password_encoder_service, jwt_service

class BaseTestCase(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def tearDown(self):
        pass

def generate_random_string():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def create_user(app, email, password, **data):
    with app.app_context():
        user = User(
            employee_id=data.get('employee_id', generate_random_string()),
            email=email,
            firstname=data.get('firstname', 'John'),
            lastname=data.get('lastname', 'Doe'),
            password=password_encoder_service.encode_password(password),
            department=data.get('department', 'College'),
            is_staff=data.get('is_staff', False),
            is_admin=data.get('is_admin', False),
            is_superuser=data.get('is_superuser', False),
            is_deleted=data.get('is_deleted', False)
        )

        db.session.add(user)
        db.session.commit()

        token = jwt_service.generate_token(user.email)
        return user.id, token
