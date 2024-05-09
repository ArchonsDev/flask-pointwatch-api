from utils import BaseTestCase

class TestRegister(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        self.uri = '/auth/register'

    def tearDown(self):
        super().tearDown()

    def test_post_success(self):
        payload = {
            'employee_id': '12-3456-789',
            'email': 'example@email.com',
            'firstname': 'John',
            'lastname': 'Doe',
            'password': 'password',
            'department': 'College'
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = self.client.post(self.uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('access_token' in data)
        self.assertTrue('user' in data)

    def test_post_fail(self):
        payload = {
            'employee_id': '12-3456-789',
            'email': 'example@email.com',
            'firstname': 'John',
            'lastname': 'Doe',
            'department': 'College'
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = self.client.post(self.uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 400)

        data = response.json

        self.assertTrue('error' in data)
