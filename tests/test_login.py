from utils import BaseTestCase, create_user

class TestLogin(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uri = '/auth/login'

        self.email = 'example@email.com'
        self.password = 'password'

        self.user_id, self.user_token = create_user(
            self.app,
            self.email,
            self.password
        )

    def tearDown(self):
        super().tearDown()

    def test_login_success(self):
        payload = {
            'email': self.email,
            'password': self.password
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = self.client.post(self.uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('access_token' in data)
        self.assertTrue('user' in data)

    def test_login_fail(self):
        payload = {
            'email': self.email,
            'password': 'asdkjhasjkDAHS'
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = self.client.post(self.uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 401)

        data = response.json

        self.assertTrue('error' in data)
