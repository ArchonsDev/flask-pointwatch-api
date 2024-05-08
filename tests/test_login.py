from unittest import TestCase

from api import create_app, db
from api.models.user import User
from api.services import password_encoder_service, jwt_service

class TestLogin(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            user = User(
                employee_id='21-4526-578',
                email='brenturiel.empasis@cit.edu',
                firstname='Brent Uriel',
                lastname='Empasis',
                password=password_encoder_service.encode_password('password'),
                department='College',
                is_admin=True
            )

            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        pass

    def test_login_success(self):
        uri = '/auth/login'

        payload = {
            'email': 'brenturiel.empasis@cit.edu',
            'password': 'password'
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = self.client.post(uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('access_token' in data)
        self.assertTrue('user' in data)

    def test_login_fail(self):
        uri = '/auth/login'

        payload = {
            'email': 'brenturiel.empasis@cit.edu',
            'password': 'asdkjhasjkDAHS'
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = self.client.post(uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 401)

        data = response.json

        self.assertTrue('error' in data)
