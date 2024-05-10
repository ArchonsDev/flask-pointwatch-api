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

 