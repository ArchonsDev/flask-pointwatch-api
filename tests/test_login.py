from unittest import TestCase

from api import create_app
from api.services import user_service

class TestLogin(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            user_service.create_user(
                '21-4526-578',
                'brenturiel.empasis@cit.edu',
                'Brent Uriel',
                'Empasis',
                'password',
                'College'
            )

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
