from unittest import TestCase

from api import create_app, db
from api.models.user import User
from api.services import password_encoder_service, jwt_service

class TestAdmin(TestCase):
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
                is_admin=True
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

    def test_get_own_user_data(self):
        uri = '/users/1'
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = self.client.get(uri, headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('id' in data)
        self.assertEqual(data.get('id'), 1)  

    def test_get_other_user_data_as_admin(self):
        uri = '/users/2'
        
        headers = {
            'Authorization': f'Bearer {self.token}'
        }

        response = self.client.get(uri, headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('id' in data)
        self.assertEqual(data.get('id'), 2)
