from unittest import TestCase

from api import create_app
from api.models import db
from api.models.user import User

class TestRegister(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        uri = '/auth/register'

        payload = {
            'employee_id': '21-4526-578',
            'email': 'brenturiel.empasis@cit.edu',
            'firstname': 'Brent Uriel',
            'lastname': 'Empasis',
            'password': 'password',
            'department': 'College'
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = self.client.post(uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

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
