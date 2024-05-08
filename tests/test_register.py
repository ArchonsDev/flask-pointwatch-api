from unittest import TestCase

from api import create_app

class TestRegister(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

    def tearDown(self):
        pass

    def test_register_success(self):
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

        data = response.json

        self.assertTrue('access_token' in data)
        self.assertTrue('user' in data)

    def test_register_fail(self):
        uri = '/auth/register'

        payload = {
            'employee_id': '21-4526-578',
            'email': 'brenturiel.empasis@cit.edu',
            'firstname': 'Brent Uriel',
            'lastname': 'Empasis',
            'department': 'College'
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = self.client.post(uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 400)

        data = response.json

        self.assertTrue('error' in data)
