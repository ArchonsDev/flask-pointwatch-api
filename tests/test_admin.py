from utils import BaseTestCase

from utils import create_user

class TestAdmin(BaseTestCase):
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
            self.user1_password,
            is_admin=True
        )

        self.user2_id, self.user2_token = create_user(
            self.app,
            self.user2_email,
            self.user2_password
        )

    def tearDown(self):
        super().tearDown()

    def test_get_own_user_data(self):  
        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.get(self.uri.format(user_id=self.user1_id), headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('id' in data)
        self.assertEqual(data.get('id'), 1)

    def test_get_other_user_data_fail(self):
        headers = {
            'Authorization': f'Bearer {self.user2_token}'
        }

        response = self.client.get(self.uri.format(user_id=self.user1_id), headers=headers)

        self.assertEqual(response.status_code, 403)

        data = response.json

        self.assertTrue('error' in data)

    def test_get_other_user_data_as_admin(self):        
        headers = {
            'Authorization': f'Bearer {self.user1_token}'
        }

        response = self.client.get(self.uri.format(user_id=self.user1_id), headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('id' in data)
        self.assertEqual(data.get('id'), self.user1_id)
