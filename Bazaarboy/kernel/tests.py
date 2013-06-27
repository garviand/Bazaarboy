"""
Unit tests for kernel
"""

import json
from django.test import TestCase
from django.test.client import Client

class UserTest(TestCase):
    """
    Tests for the user controller
    """
    def test_authentication(self):
        # Test register
        client = Client()
        response = client.get('/user/create/')
        self.assertEqual(response.status_code, 405)
        response = client.post('/user/create/')
        self.assertEqual(response.status_code, 400)
        params = {
            'email':'test@bazaarboy.com',
            'password':'123456',
            'confirm':'123456',
            'city':1
        }
        response = client.post('/user/create/', params)
        self.assertEqual(response.status_code, 200)
        jsonRes = json.loads(response.content)
        self.assertEqual(jsonRes['status'], 'OK')
        response = client.post('/user/create/', params)
        self.assertEqual(response.status_code, 403)