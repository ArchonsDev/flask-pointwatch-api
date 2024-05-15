from utils import BaseTestCase, create_user, create_term, get_test_file

class TestSWTDValidation(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uri = '/swtds/'
        
        # Create a user and a term for use in tests
        self.user_email = 'testuser@email.com'
        self.user_password = 'securepassword'
        self.user_id, self.user_token = create_user(self.app, self.user_email, self.user_password)
        self.term_id = create_term(self.app, '2nd Semester 2024', '02-01-2024', '06-30-2024')
        self.test_file = get_test_file()

        # Create an SWTD form which will be used in the validation tests
        post_headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        post_data = {
            'author_id': str(self.user_id),
            'title': 'Test SWTD',
            'category': 'Workshop',
            'venue': 'Virtual',
            'role': 'Participant',
            'date': '02-15-2024',
            'time_started': '10:00',
            'time_finished': '12:00',
            'points': 10,
            'benefits': 'Gain insights',
            'term_id': str(self.term_id),
            'proof': self.test_file
        }
        response = self.client.post(self.uri, headers=post_headers, data=post_data)
        self.swtd_id = response.json['id']
        self.validation_uri = f'{self.uri}{self.swtd_id}/validation/'

    def get_validation_details(self, form_id):
        swtd = self.swtd_service.get_swtd(form_id)
        if swtd is None:
            raise SWTDFormNotFoundError()

        if swtd.validation is None:
            return self.build_response({'status': 'PENDING'})  # Default status if no validation record exists

        return self.build_response(swtd.validation.to_dict(), 200)

    def update_validation_status(self, form_id, status):
        swtd = self.swtd_service.get_swtd(form_id)
        if swtd is None:
            raise SWTDFormNotFoundError()

        if swtd.validation is None:
            raise ResourceNotFoundError("Validation record not found.")  # Custom exception for missing validation

        # Proceed with updating the validation record
        self.swtd_validation_service.update_validation(swtd, status)
        return self.build_response({'status': status}, 200)


    def test_retrieve_swtd_form_validation_proof(self):
        headers = {'Authorization': f'Bearer {self.user_token}'}
        proof_uri = f'{self.validation_uri}proof'
        response = self.client.get(proof_uri, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.data, bytes))  # Check that the response contains binary data (the proof file)

    def test_update_swtd_form_validation_proof(self):
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        new_test_file = get_test_file()  # Assume a different file for the update
        update_data = {'proof': new_test_file}
        proof_uri = f'{self.validation_uri}proof'
        response = self.client.put(proof_uri, headers=headers, data=update_data)
        self.assertEqual(response.status_code, 200)
        # Additional assertions can be made here depending on how the proof update is confirmed via the API

    def tearDown(self):
        super().tearDown()

    # Negative test cases
    def test_get_swtd_form_validation_details_non_existent_form(self):
        headers = {'Authorization': f'Bearer {self.user_token}'}
        non_existent_form_uri = f'{self.uri}99999/validation/'
        response = self.client.get(non_existent_form_uri, headers=headers)
        self.assertEqual(response.status_code, 500)

    def test_update_swtd_form_validation_status_with_invalid_status(self):
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'application/json'
        }
        invalid_update_data = {'status': 'UNKNOWN'}
        response = self.client.put(self.validation_uri, headers=headers, json=invalid_update_data)
        self.assertEqual(response.status_code, 500)

    def test_retrieve_swtd_form_validation_proof_with_unauthorized_user(self):
        # Assuming that a different user token is required for unauthorized access
        unauthorized_headers = {'Authorization': 'Bearer invalid_or_expired_token'}
        proof_uri = f'{self.validation_uri}proof'
        response = self.client.get(proof_uri, headers=unauthorized_headers)
        self.assertEqual(response.status_code, 422)

    def test_update_swtd_form_validation_proof_with_invalid_file(self):
        headers = {
            'Authorization': f'Bearer {self.user_token}',
            'Content-Type': 'multipart/form-data'
        }
        invalid_update_data = {}  # Missing 'proof' key
        proof_uri = f'{self.validation_uri}proof'
        response = self.client.put(proof_uri, headers=headers, data=invalid_update_data)
        self.assertEqual(response.status_code, 400)
