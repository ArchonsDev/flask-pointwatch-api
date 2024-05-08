from unittest import TestCase

from api import create_app, db
from api.models.user import User
from api.services import password_encoder_service, jwt_service

class TestUser(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

        with self.app.app_context():
            user1 = User(
                employee_id='21-4526-578',
                email='brenturiel.empasis@cit.edu',
                firstname='Brent Uriel',
                lastname='Empasis',
                password=password_encoder_service.encode_password('password'),
                department='College',
            )

            user2 = User(
                employee_id='12-3456-789',
                email='example@email.com',
                firstname='John',
                lastname='Doe',
                password=password_encoder_service.encode_password('password'),
                department='College'
            )

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

        with self.app.app_context():
            self.token = jwt_service.generate_token('brenturiel.empasis@cit.edu')

    def tearDown(self):
        pass

    def test_get_user_success(self):
        uri = '/users/1'

        headers = {
            'Authorization': f'Bearer {self.token}'
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

        self.assertEqual(response.status_code, 403)

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
