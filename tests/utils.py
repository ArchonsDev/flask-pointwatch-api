import random
import string
import io
import os

from unittest import TestCase
from datetime import datetime
from werkzeug.datastructures import FileStorage

from api import db, create_app
from api.models.user import User
from api.models.term import Term
from api.services import password_encoder_service, jwt_service, term_service

class BaseTestCase(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def tearDown(self):
        # Define the path to the file
        base_path = os.path.abspath('data')
        file_path = os.path.join(base_path, '1', '1', 'testfile.txt')

        # Check if the file exists before attempting to delete it
        if os.path.exists(file_path):
            os.remove(file_path)

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

def create_term(app, name, start_date, end_date, is_deleted=False):
    with app.app_context():
        term = Term(
            name=name,
            start_date=datetime.strptime(start_date, '%m-%d-%Y'),
            end_date=datetime.strptime(end_date, '%m-%d-%Y'),
            is_deleted=is_deleted
        )

        db.session.add(term)
        db.session.commit()

        return term.id

def get_test_file():
    content = b'Lorem ipsum'
    stream = io.BytesIO(content)
    file = FileStorage(stream, filename='testfile.txt')
    return file
