from utils import BaseTestCase, create_user
from api import create_app

class TestResetPassword(BaseTestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        super().setUp()
        
    
        self.uri = '/auth/resetpassword'

        self.user1_email ='user1@email.com'
        self.user1_password = "password"

        self.user1_id, self.user1_token = create_user(
            self.app,
            self.user1_email,
            self.user1_password
        )

    def tearDown(self):
        super().tearDown()

    def test_reset_password_success(self):
 
        headers = {
            'Authorization': f'Bearer {self.user1_token}',
            "Content-Type": "application/json"
        }
        payload ={
            'password': 'password'
        }
        
        response = self.client.post(self.uri, headers=headers, json=payload)
        self.assertTrue(response.status_code, 200)
        
        data = response.json
        self.assertTrue((['message']), "Password changed.")

def test_reset_password_fail(self):
 
        headers = {
            'Authorization': f'Bearer {self.user1_token}',
            "Content-Type": "application/json"
        }
        payload ={
            'email': 'user1@email.com',
            'password': 'password'
        }
        
        response = self.client.post(self.uri, headers=headers, json=payload)
        self.assertEqual(response.status_code, 500)
        
        data = response.json
        self.assertTrue((['error']), "Invalid Parameter <name>")


    