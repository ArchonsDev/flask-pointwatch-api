from utils import BaseTestCase, create_user, create_term, get_test_file

class TestSWTD(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uri = '/swtds/'
        # First user setup
        self.user_email = 'example@email.com'
        self.user_password = 'password'
        self.test_file = get_test_file()
        self.user_id, self.user_token = create_user(self.app, self.user_email, self.user_password)

        # Second user setup
        self.user_email2 = 'second@example.com'
        self.user_password2 = 'password2'
        self.user_id2, self.user_token2 = create_user(self.app, self.user_email2, self.user_password2)


    def tearDown(self):
        super().tearDown()

    def test_delete_swtd(self):
        # Submitting an SWTD form
        self.term_id = create_term(self.app, '1st Semester 2324', '01-24-2024', '05-30-2024')
        post_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        post_data = {
            'author_id': str(self.user_id),
            'title': 'Delete Test SWTD',
            'category': 'Seminar',
            'venue': 'Online',
            'role': 'Attendee',
            'date': '01-23-2024',
            'time_started': '00:00',
            'time_finished': '01:00',
            'points': 5,
            'benefits': 'This is a test entry for deletion.',
            'term_id': str(self.term_id),
            'proof': self.test_file
        }
        post_response = self.client.post(self.uri, headers=post_headers, data=post_data)
        self.assertEqual(post_response.status_code, 200)
        swtd_id = post_response.json['id']

        # Deleting the SWTD form
        delete_headers = {
            'Authorization': f'Bearer {self.user_token}'
        }
        delete_response = self.client.delete(f"{self.uri}{swtd_id}", headers=delete_headers)
        self.assertEqual(delete_response.status_code, 200)

        # Trying to retrieve the deleted SWTD form
        get_response = self.client.get(f"{self.uri}{swtd_id}", headers=delete_headers)
        self.assertNotEqual(get_response.status_code, 200)
        # Optionally check for a specific response code or message indicating the resource does not exist
        # For example:
        # self.assertEqual(get_response.status_code, 404)

    def test_delete_swtd_negative(self):
        # Assuming 9999 is a non-existent ID for the negative test case
        invalid_swtd_id = 9999  
        delete_headers = {
            'Authorization': f'Bearer {self.user_token}'
        }

        # Trying to delete an SWTD form with an invalid ID
        delete_response = self.client.delete(f"{self.uri}{invalid_swtd_id}", headers=delete_headers)
        self.assertEqual(delete_response.status_code, 404)  # Expecting a 'Not Found' status code

        # Trying to delete an SWTD form without authorization token
        delete_response_no_auth = self.client.delete(f"{self.uri}{invalid_swtd_id}")
        self.assertEqual(delete_response_no_auth.status_code, 401)  # Expecting an 'Unauthorized' status code

        # Trying to delete an SWTD form with an expired or invalid token
        expired_token = 'this.is.an.expired.token'
        delete_headers['Authorization'] = f'Bearer {expired_token}'
        delete_response_invalid_token = self.client.delete(f"{self.uri}{invalid_swtd_id}", headers=delete_headers)
        self.assertEqual(delete_response_invalid_token.status_code, 422)  # Expecting an 'Unauthorized' status code

        # Assuming self.user_token2 is a token for a different user who does not have admin privileges
        # You need to setup self.user_token2 in the setUp method or within this test
        delete_headers['Authorization'] = f'Bearer {self.user_token2}'
        delete_response_unauthorized_user = self.client.delete(f"{self.uri}{invalid_swtd_id}", headers=delete_headers)
        self.assertEqual(delete_response_unauthorized_user.status_code, 404)  # Expecting a 'Forbidden' status code





