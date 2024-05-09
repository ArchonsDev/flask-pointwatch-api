from utils import BaseTestCase, create_user
class TestUser(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uri = '/users/{user_id}'

        self.user1_email = 'user1@email.com'
        self.user1_password = 'password'
        
        self.user2_email = 'user2@email.com'
        self.user2_password = 'password'

        self.user1_id, self.user1_token = create_user(
            self.app,
            self.user1_email,
            self.user1_password
        )

        self.user2_id, self.user2_token = create_user(
            self.app,
            self.user2_email,
            self.user2_password
        )

    def tearDown(self):
        super().tearDown()

    def test_get_user_success(self):
        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.get(self.uri.format(user_id=self.user1_id), headers=headers)

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
        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.get(self.uri.format(user_id=self.user2_id), headers=headers)

        self.assertEqual(response.status_code, 403)

        data = response.json

        self.assertTrue('error' in data)

    def test_put_user_success(self):
        payload = {
            'firstname': 'X',
            'lastname': 'X',
            'department': 'X'
        }

        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.put(self.uri.format(user_id=self.user1_id), headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertEqual(data.get('firstname'), 'X')
        self.assertEqual(data.get('lastname'), 'X')
        self.assertEqual(data.get('department'), 'X')

    def test_delete_user_success(self):
        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.delete(self.uri.format(user_id=self.user1_id), headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('message' in data)
