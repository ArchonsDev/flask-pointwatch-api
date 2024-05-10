from utils import BaseTestCase
from your_application.exceptions import UserNotFoundError

class TestResetPassword(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        # URI for the reset password endpoint
        self.uri = '/auth/resetpassword'
        
        # Create a user in the database for testing
        self.user = self.user_service.create_user(
            employee_id='12-3456-789',
            email='example@email.com',
            firstname='John',
            lastname='Doe',
            password='initialPassword',
            department='College'
        )

        # Login to generate a valid token for the user
        self.valid_token = self.jwt_service.generate_token(self.user.email)

    def tearDown(self):
        super().tearDown()

    def test_reset_password_success(self):
        # Simulate a logged-in user by providing a valid JWT
        headers = {
            "Authorization": f"Bearer {self.valid_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            'password': 'newPassword123'
        }
        
        response = self.client.post(self.uri, headers=headers, json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json
        self.assertEqual(data['message'], "Password changed.")

    def test_reset_password_no_user_found(self):
        # Use a JWT for a non-existent user
        invalid_token = self.jwt_service.generate_token('nonexistent@email.com')
        headers = {
            "Authorization": f"Bearer {invalid_token}",
            "Content-Type": "application/json"
        }

        payload = {
            'password': 'newPassword123'
        }

        response = self.client.post(self.uri, headers=headers, json=payload)
        self.assertEqual(response.status_code, 404)
        
        data = response.json
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'User not found')

    def test_reset_password_missing_field(self):
        headers = {
            "Authorization": f"Bearer {self.valid_token}",
            "Content-Type": "application/json"
        }

        # Missing 'password' field in payload
        payload = {}

        response = self.client.post(self.uri, headers=headers, json=payload)
        self.assertEqual(response.status_code, 400)
        
        data = response.json
        self.assertTrue('error' in data)
        self.assertEqual(data['error'], 'Missing required field: password')
