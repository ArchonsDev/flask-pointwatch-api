from unittest import TestCase

from api import create_app
from api.services import user_service, jwt_service

class TestUser(TestCase):
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

    def test_get_user_success(self):
        uri = '/users/1'

        with self.app.app_context():
            token = jwt_service.generate_token('brenturiel.empasis@cit.edu')

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get(uri, headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        fields = [
            'id',
            'employee_id',
            'email',
            'firstname',
            'lastname',
            'password',
            'department',
            'is_staff',
            'is_admin',
            'is_superuser',
            'is_deleted'
        ]

        for field in fields:
            self.assertTrue(field in data)

    def test_get_user_fail(self):
        uri = '/users/2'

        with self.app.app_context():
            token = jwt_service.generate_token('brenturiel.empasis@cit.edu')

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.get(uri, headers=headers)

        self.assertEqual(response.status_code, 404)

        data = response.json

        self.assertTrue('error' in data)

    def test_update_user_success(self):
        uri = '/users/1'

        with self.app.app_context():
            token = jwt_service.generate_token('brenturiel.empasis@cit.edu')

        payload = {
            'firstname': 'X',
            'lastname': 'X',
            'department': 'X'
        }

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.put(uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertEqual(data.get('firstname'), 'X')
        self.assertEqual(data.get('lastname'), 'X')
        self.assertEqual(data.get('department'), 'X')

    def test_delete_user_success(self):
        uri = '/users/1'

        with self.app.app_context():
            token = jwt_service.generate_token('brenturiel.empasis@cit.edu')

        headers = {
            'Authorization': f'Bearer {token}'
        }

        response = self.client.delete(uri, headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('message' in data)
