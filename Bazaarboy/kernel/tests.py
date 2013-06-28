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
    fixtures = ['tests.json']

    def test_register(self):
        client = Client()
        # Should not allow methods other than POST
        response = client.get('/user/create/')
        self.assertEqual(response.status_code, 405)
        # Should check if the required params are present
        response = client.post('/user/create/')
        self.assertEqual(response.status_code, 400)
        # Should not allow an existing email to register
        params = {
            'email':'handy@andy.com',
            'password':'123456',
            'confirm':'123456',
            'city':1
        }
        response = client.post('/user/create/', params)
        jsonRes = json.loads(response.content)
        self.assertEqual(jsonRes['status'], 'FAIL')
        # Should be able to register normally
        params['email'] = 'nothandy@andy.com'
        response = client.post('/user/create/', params)
        jsonRes = json.loads(response.content)
        self.assertEqual(jsonRes['status'], 'OK')
        # Should not allow register if a session exists
        response = client.post('/user/create/', params)
        self.assertEqual(response.status_code, 403)

    def test_login(self):
        client = Client()
        # Should not allow methods other than GET
        response = client.post('/user/auth/')
        self.assertEqual(response.status_code, 405)
        # Should check if the required params are present
        response = client.get('/user/auth/')
        self.assertEqual(response.status_code, 400)
        # Should check email/password combo
        params = {
            'email':'handy@andy.com',
            'password':'abcdefg' # Correct password is 123456
        }
        response = client.get('/user/auth/', params)
        jsonRes = json.loads(response.content)
        self.assertEqual(jsonRes['status'], 'FAIL')
        # Should be able to login normally
        params['password'] = 123456
        response = client.get('/user/auth/', params)
        jsonRes = json.loads(response.content)
        self.assertEqual(jsonRes['status'], 'OK')
        # Should not allow login if a session exists
        response = client.get('/user/auth/', params)
        self.assertEqual(response.status_code, 403)