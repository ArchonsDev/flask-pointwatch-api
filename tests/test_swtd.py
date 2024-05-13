from utils import BaseTestCase, create_user, create_term, get_test_file

class TestSWTD(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.uri = '/swtds/'

        self.user_email = 'example@email.com'
        self.user_password = 'password'
        self.test_file = get_test_file()

        self.user_id, self.user_token = create_user(
            self.app,
            self.user_email,
            self.user_password
        )

    def tearDown(self):
        super().tearDown()

    def test_post_swtd(self):
        self.term_id = create_term(self.app, '1st Semster 2324', '01-24-2024', '05-30-2024')
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }

        data = {
            'author_id': str(self.user_id),
            'title': 'Sample SWTD',
            'category': 'Seminar',
            'venue': 'Online',
            'role': 'Attendee',
            'date': '01-23-2024',
            'time_started': '00:00',
            'time_finished': '01:00',
            'points': 5,
            'benefits': 'Lorem Ipsum',
            'term_id': str(self.term_id),
            'proof': self.test_file
        }

        response = self.client.post(self.uri, headers=headers, data=data)

        self.assertEqual(response.status_code, 200)

         # Retrieving the list of SWTD forms to verify the newly submitted form is present
        get_headers = {
            'Authorization': f'Bearer {self.user_token}'
        }
        get_params = {
            'author_id': str(self.user_id)  # Filtering by author ID to simplify checking
        }
        response = self.client.get(self.uri, headers=get_headers, query_string=get_params)
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertTrue('swtds' in data and len(data['swtds']) > 0)
        found = any(swtd['title'] == 'Sample SWTD' for swtd in data['swtds'])
        self.assertTrue(found, "Submitted SWTD form should be in the retrieved list")
