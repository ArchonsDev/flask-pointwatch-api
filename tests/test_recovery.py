from unittest import TestCase

from api import create_app, db
from api.models.user import User

class TestRecovery(TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()

def tearDown(self):
    pass

def test_recovery_success(self):
    uri = '/auth/recovery'

    payload = {
        'email': 'fritzselerio.navarro@yahoo.com'
    }

    headers = {
        "Content-Type": "application/json"
     }
    

    response = self.client.post(uri, headers=headers, json=payload)

    self.assertEqual(response.status_code, 200)

    data = response.json

    self.assertTrue(data['message']), 'Please check email for instructions on how to reset your password.'


def test_recovery_fail(self):
    uri = '/auth/recovery'

    payload = {
        'email': ''
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = self.client.post(uri, headers=headers, json=payload)

    # Assuming a failure would return a 400 status code (Bad Request)
    self.assertEqual(response.status_code, 400)

    data = response.json

    # Check that the 'Error' key is in the response data and contains the expected message
    self.assertIn('Error', data)
    self.assertEqual(data['Error'], 'Place your email account.')
