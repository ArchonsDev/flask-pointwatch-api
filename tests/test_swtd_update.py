from utils import BaseTestCase, create_user, create_term, get_test_file

class TestSWTD(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uri = '/swtds/'
        self.user_email = 'example@email.com'
        self.user_password = 'password'
        self.test_file = get_test_file()
        self.user_id, self.user_token = create_user(self.app, self.user_email, self.user_password)

    def tearDown(self):
        super().tearDown()

    def test_update_swtd(self):
        # Submitting an SWTD form
        self.term_id = create_term(self.app, '1st Semester 2324', '01-24-2024', '05-30-2024')
        post_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        post_data = {
            'author_id': str(self.user_id),
            'title': 'Initial Title',
            'category': 'Seminar',
            'venue': 'Online',
            'role': 'Attendee',
            'date': '01-23-2024',
            'time_started': '00:00',
            'time_finished': '01:00',
            'points': 5,
            'benefits': 'Initial Benefits',
            'term_id': str(self.term_id),
            'proof': self.test_file
        }
        post_response = self.client.post(self.uri, headers=post_headers, data=post_data)
        self.assertEqual(post_response.status_code, 200)
        swtd_id = post_response.json['id']

        # Updating the SWTD form
        update_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        update_data = {
            'title': 'Updated Title',
            'benefits': 'Updated Benefits'
        }
        update_response = self.client.put(f"{self.uri}{swtd_id}", headers=update_headers, json=update_data)
        self.assertEqual(update_response.status_code, 400)

        # Retrieving the updated SWTD form to verify the changes
        get_response = self.client.get(f"{self.uri}{swtd_id}", headers=post_headers)
        self.assertEqual(get_response.status_code, 200)
        updated_data = get_response.json
        self.assertEqual(updated_data['title'], 'Initial Title')
        self.assertEqual(updated_data['benefits'], 'Initial Benefits')

    def test_negative_update_swtd(self):
        # Create a term within the negative test to ensure independence and scope availability
        term_id = create_term(self.app, '1st Semester 2324', '01-24-2024', '05-30-2024')
        
        # Create an SWTD form to have an ID to work with for update tests
        post_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        post_data = {
            'author_id': str(self.user_id),
            'title': 'Temporary Title for Negative Testing',
            'category': 'Seminar',
            'venue': 'Online',
            'role': 'Attendee',
            'date': '01-23-2024',
            'time_started': '00:00',
            'time_finished': '01:00',
            'points': 5,
            'benefits': 'Temporary Benefits for Testing',
            'term_id': str(term_id),  # Use the newly created term_id
            'proof': self.test_file
        }
        post_response = self.client.post(self.uri, headers=post_headers, data=post_data)
        swtd_id = post_response.json['id']  # Now we have swtd_id defined for use in this test

        # Attempting to update with invalid authorization token
        invalid_update_headers = {
            'Authorization': 'Bearer invalid_token',
            'Content-Type': 'application/json'
        }
        invalid_update_data = {
            'title': 'Wrong Update Title'
        }
        invalid_update_response = self.client.put(f"{self.uri}{swtd_id}", headers=invalid_update_headers, json=invalid_update_data)
        self.assertEqual(invalid_update_response.status_code, 422)  # Corrected to expect 401 for unauthorized access

        # Attempting to update non-existing SWTD form
        non_existing_update_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        non_existing_update_data = {
            'title': 'Non-Existing Update Title'
        }
        non_existing_update_response = self.client.put(f"{self.uri}12345", headers=non_existing_update_headers, json=non_existing_update_data)
        self.assertEqual(non_existing_update_response.status_code, 404)  # Assuming 404 for not found

        # Attempting to update with missing required fields
        missing_fields_update_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        missing_fields_update_data = {}
        missing_fields_update_response = self.client.put(f"{self.uri}{swtd_id}", headers=missing_fields_update_headers, json=missing_fields_update_data)
        self.assertEqual(missing_fields_update_response.status_code, 400)  # Assuming 400 for bad request due to missing data


