from utils import BaseTestCase, create_user

class TestTerm(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uri = '/terms/'

        self.user_email = 'example@email.com'
        self.user_password = 'password'

        self.user_id, self.user_token = create_user(
            self.app,
            self.user_email,
            self.user_password,
            is_admin=True,
        )

    def tearDown(self):
        super().tearDown()

    def test_post_term(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.user_token}'
        }

        payload = {
            'name': '1st Semester S.Y. 2023-2024',
            'start_date': '01-24-2024',
            'end_date': '05-30-2024'
        }

        response = self.client.post(self.uri, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200)
        
        data = response.json

        self.assertTrue('id' in data)
        self.assertTrue('name' in data)
        self.assertTrue('start_date' in data)
        self.assertTrue('end_date' in data)

        self.assertEqual(data.get('name'), '1st Semester S.Y. 2023-2024')
        self.assertEqual(data.get('start_date'), '01-24-2024')
        self.assertEqual(data.get('end_date'), '05-30-2024')

    def test_get_all_terms(self):
        self.test_post_term()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.user_token}'
        }

        response = self.client.get(self.uri, headers=headers)

        self.assertEqual(response.status_code, 200)

        data = response.json

        self.assertTrue('terms' in data)
        self.assertEqual(len(data.get('terms')), 1)
