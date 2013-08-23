"""
Unit tests for kernel
"""

import json
from django.test import TestCase
from django.test.client import Client
from src.email import Email
from models import *

import pdb

class EmailTest(TestCase):
    """
    Tests for email utilities
    """
    fixtures = ['tests.json']

    def test_confirmation_email(self):
        email_client = Email()
        user = User.objects.get(id = 3)
        user_confirmation = User_confirmation_code.objects.get(user = user)
        user_reset = User_reset_code.objects.get(user = user)
        response = email_client.sendConfirmationEmail(user_confirmation, user_reset, user)
        self.assertEqual(response[0]['status'], 'sent')

    def test_reset_email(self):
        email_client = Email()
        user = User.objects.get(id = 3)
        user_reset = User_reset_code.objects.get(user = user)
        response = email_client.sendResetRequestEmail(user_reset, user)
        self.assertEqual(response[0]['status'], 'sent')

    def test_password_changed_email(self):
        email_client = Email()
        user = User.objects.get(id = 3)
        response = email_client.sendPasswordChangedEmail(user)
        self.assertEqual(response[0]['status'], 'sent')

    def test_purchase_confirmation_email(self):
        email_client = Email()
        purchase = Purchase.objects.get(id = 1)
        response = email_client.sendPurchaseConfirmationEmail(purchase)
        self.assertEqual(response[0]['status'], 'sent')

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
            'full_name':'Handy Andy',
            'confirm':'123456',
            'city':1
        }
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow invalid email address
        params['email'] = 'nothandyatandy.com'
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Set VALID email to test password      
        params['email'] = 'nothandy@andy.com'
        # Should not allow short password (<6)
        params['password'] = '12345'
        params['confirm'] = '12345'
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow long password (>16)
        params['password'] = '12345678901234567'
        params['confirm'] = '12345678901234567'
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Set VALID password to test city
        params['password'] = '123456'
        params['confirm'] = '123456'
        # Should not allow nonexistent city
        params['city'] = 999999999999999999999999999
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to register normally
        params['city'] = 1
        response = json.loads(client.post('/user/create/', params).content)
        self.assertEqual(response['status'], 'OK')
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
        response = json.loads(client.get('/user/auth/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to login normally
        params['password'] = 123456
        response = json.loads(client.get('/user/auth/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not allow login if a session exists
        response = client.get('/user/auth/', params)
        self.assertEqual(response.status_code, 403)

def loggedInClient():
    client = Client()
    loginParams = {
        'email':'handy@andy.com',
        'password':'123456'
    }
    client.get('/user/auth/', loginParams)
    return client

class ProfileTest(TestCase):
    """
    Tests for the profile controller
    """
    fixtures = ['tests.json']

    def test_create(self):
        client = Client()
        # Should not be able to create unless logged in
        params = {
            'name':'Washington University',
            'description':'World class private research university',
            'community':1,
            'category':'School',
            'latitude':38.648,
            'longitude':-90.305,
            'wepay':1
        }
        response = client.post('/profile/create/', params)
        self.assertEqual(response.status_code, 403)
        # Should be able to create if logged in
        client = loggedInClient()
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not be able to create if name/description/category is too long
        params['category'] = '01234567'
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not allow nonexistent community
        params['category'] = 'School' # VALID category
        params['community'] = 999999999999
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow latitude (<-90) or (>90)
        params['community'] = 1 # VALID community
        params['latitude'] = -91
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['latitude'] = 91
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow longitude (<-180) or (>180)
        params['latitude'] = 38.648 # VALID latitude
        params['longitude'] = -181
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['longitude'] = 181
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow if not WePay owner
        params['longitude'] = -90.305 # VALID longitude
        params['wepay'] = 2
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should allow if params are correct
        params['wepay'] = 1 # VALID wepay
        response = json.loads(client.post('/profile/create/', params).content)
        self.assertEqual(response['status'], 'OK')

class EventTests(TestCase):
    """
    Tests for normal events
    """
    fixtures = ['tests.json']

    def test_create(self):
        client = loggedInClient()
        # Should check the profile existence
        params = {
        'profile':3,
        'name':'Thursday Happy Hour at BlueHill',
        'description':'An open bar celebration at BlueHill',
        'start_time':'2013-12-31 23:00:00',
        'end_time':'2014-01-01 01:00:00',
        'location':'Blueberry Hill',
        'latitude':38.655833,
        'longitude':-90.305,
        'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should check the profile ownership
        params['profile'] = 1 # not owner
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow latitude (<-90) or (>90)
        params['profile'] = 2 # VALID owner
        params['latitude'] = -91
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['latitude'] = 91
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow longitude (<-180) or (>180)
        params['latitude'] = 38.655833 # VALID latitude
        params['longitude'] = -181
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['longitude'] = 181
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to create normal event
        params['longitude'] = -90.305 # VALID longitude
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')

    def test_edit(self):
        client = loggedInClient()
        # CREATE EVENT FOR EDITING
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # Should be able to edit an event
        params = {
            'id': event,
            'name':'Thursday Happy Hour at Nico',
            'description':'An open bar celebration at Nico',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Nico',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not allow latitude (<-90) or (>90)
        params['latitude'] = -91
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['latitude'] = 91
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow longitude (<-180) or (>180)
        params['latitude'] = 38.655833 # VALID latitude
        params['longitude'] = -181
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        params['longitude'] = 181
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow blank name
        params['longitude'] = -90.305 # VALID longitude
        params['name'] = ''
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow blank description
        params['name'] = 'something' # VALID name
        params['description'] = ''
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow edits to started event
        params['description'] = 'something' # VALID location
        params['start_time'] = '2013-01-31 23:00:00'
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not allow end time before start time
        params['start_time'] = '2013-12-30 23:00:00'
        params['end_time'] = '2013-11-30 23:00:00'
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should allow end time after start time
        params['start_time'] = '2013-11-30 23:00:00' # VALID start time
        params['end_time'] = '2013-12-30 23:00:00' # VALID end time
        response = json.loads(client.post('/event/edit/', params).content)
        self.assertEqual(response['status'], 'OK')
        

    def test_launch(self):
        client = loggedInClient()
        # CREATE EVENT FOR LAUNCH
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # Should be able to launch an event
        params = {
            'id':event
        }
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not be able to launch a nonexistent event
        params = {
            'id':9999999
        }
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # CREATE EVENT FOR LAUNCH THAT HAS ALREADY STARTED
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at Three Kings',
            'description':'An open bar celebration at Three Kings',
            'start_time':'2013-01-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Three Kings',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # Should not be able to launch a started event
        params = {
            'id':event
        }
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to delaunch an event
    def test_delaunch(self):
        client = loggedInClient()
        # CREATE EVENT FOR DELAUNCH
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # LAUNCH EVENT FOR DELAUNCH
        params['id'] = event
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should be able to delaunch an event
        response = json.loads(client.post('/event/delaunch/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not be able to delaunch an unlaunched event
        response = json.loads(client.post('/event/delaunch/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to delaunch a nonexistent event
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'OK')
        params['id'] = 9999999
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # CREATE EVENT FOR DELAUNCH THAT HAS ALREADY STARTED
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at Three Kings',
            'description':'An open bar celebration at Three Kings',
            'start_time':'2013-01-30 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Three Kings',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social',
            'is_launched':True
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # Should not be able to delaunch a started event
        params = {
            'id':event
        }
        response = json.loads(client.post('/event/delaunch/', params).content)
        self.assertEqual(response['status'], 'FAIL')

    def test_delete(self):
        client = loggedInClient()
        # CREATE EVENT FOR DELETION
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # LAUNCH EVENT FOR DELETION (SHOULD FAIL)
        params['id'] = event
        response = json.loads(client.post('/event/launch/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not be able to delete a launched event
        response = json.loads(client.post('/event/delete/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # DELAUNCH EVENT FOR DELETION
        params['id'] = event
        response = json.loads(client.post('/event/delaunch/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should be able to delete a delaunched event
        response = json.loads(client.post('/event/delete/', params).content)
        self.assertEqual(response['status'], 'OK')

    def test_create_ticket(self):
        client = loggedInClient()
        # CREATE EVENT FOR TICKETS
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # Should be able to create a ticket
        params = {
            'event':event,
            'name':'Regular',
            'description':'Regular admission ticket',
            'price':20.00,
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')
        # Should NOT be able to create a ticket with end time < start time
        params = {
            'event':event,
            'name':'Late',
            'description':'Late admission ticket',
            'price':35.00,
            'start_time':'2013-12-28 00:00:00',
            'end_time':'2013-12-27 00:00:00'
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'FAIL')
        # Should NOT be able to create a ticket with price < 0
        params = {
            'event':event,
            'name':'Already Started',
            'description':'This event happened in 2012',
            'price':-35.00,
            'start_time':'2012-12-28 00:00:00'
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'FAIL')
        # Should NOT be able to create a ticket with quantity < 0
        params = {
            'event':event,
            'name':'Already Started',
            'description':'This event happened in 2012',
            'price':35.00,
            'start_time':'2012-12-28 00:00:00',
            'quantity': -5
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'FAIL')
        # Should NOT be able to create a ticket with start_time > event.start_time
        params = {
            'event':event,
            'name':'Already Started',
            'description':'This event happened in 2012',
            'price':35.00,
            'start_time':'2013-12-31 23:00:01' # event = 2013-12-31 23:00:00
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to create a ticket with start time
        params = {
            'event':event,
            'name':'Late',
            'description':'Late admission ticket',
            'price':35.00,
            'start_time':'2013-12-28 00:00:00'
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['ticket']['start_time'], 
                         params['start_time'])
        # Should be able to create a ticket with end time
        params = {
            'event':event,
            'name':'Early bird',
            'description':'Early bird admission ticket',
            'price':15.00,
            'end_time':'2013-12-28 00:00:00'
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')
        self.assertEqual(response['ticket']['end_time'], 
                         params['end_time'])

    def test_edit_ticket(self):
        client = loggedInClient()
        # CREATE EVENT FOR TICKETS
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # CREATE TICKET FOR EDITING
        params = {
            'event':event,
            'name':'Regular',
            'description':'Regular admission ticket',
            'price':20.00
        }
        response = client.post('/event/ticket/create/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')
        # Should be able to edit a ticket
        params = {
            'id':response['ticket']['pk'],
            'name':'Regular',
            'description':'Regular admission ticket WITH EDITS',
            'price':20.00,
        }
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should not be able to edit a ticket with blank name
        params['name'] = ''
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to edit a ticket with blank description
        params['name'] = 'something'
        params['description'] = ''
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to edit a ticket with price < 0
        params['description'] = 'something'
        params['price'] = -1
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to edit a ticket with quantity < 0
        params['price'] = 20
        params['quantity'] = -1
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to edit a ticket with start_time > event.start_time
        params['quantity'] = 20
        params['start_time'] = '2013-12-31 23:00:01'
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should not be able to edit a ticket with end_time < start_time
        params['start_time'] = '2013-12-31 23:00:01'
        params['end_time'] = '2013-12-31 23:00:00'
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        self.assertEqual(response['status'], 'FAIL')
        # Should be able to edit a ticket with end_time > start_time
        params['start_time'] = '2012-12-31 23:00:00'
        params['end_time'] = '2012-12-31 23:00:01'
        response = json.loads(client.post('/event/ticket/edit/', params).content)
        #pdb.set_trace()
        self.assertEqual(response['status'], 'OK')

    def test_delete_ticket(self):
        client = loggedInClient()
        # CREATE EVENT FOR TICKETS
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # CREATE TICKET FOR DELETION
        params = {
            'event':event,
            'name':'Regular',
            'description':'Regular admission ticket',
            'price':20.00
        }
        response = json.loads(client.post('/event/ticket/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        # Should be able to delete a ticket
        params = {
            'id':response['ticket']['pk']
        }
        response = client.post('/event/ticket/delete/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')

    def test_purchase(self):
        client = loggedInClient()
        # CREATE EVENT FOR TICKETS
        params = {
            'profile':2,
            'name':'Thursday Happy Hour at BlueHill',
            'description':'An open bar celebration at BlueHill',
            'start_time':'2013-12-31 23:00:00',
            'end_time':'2014-01-01 01:00:00',
            'location':'Blueberry Hill',
            'latitude':38.655833,
            'longitude':-90.305,
            'category':'Social'
        }
        response = json.loads(client.post('/event/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        event = response['event']['pk']
        # CREATE TICKET FOR PURCHASE
        params = {
            'event':event,
            'name':'Regular',
            'description':'Regular admission ticket',
            'price':20.00,
            'quantity':100
        }
        response = json.loads(client.post('/event/ticket/create/', params).content)
        self.assertEqual(response['status'], 'OK')
        ticket = response['ticket']['pk']
        # Should not be able to purchase a ticket to an unlaunched event
        params['ticket'] = ticket
        response = client.post('/event/purchase/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'FAIL')
        # LAUNCH EVENT
        params['id'] = event
        response = client.post('/event/launch/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')
        # Should be able to purchase a ticket after launch
        response = client.post('/event/purchase/', params).content
        response = json.loads(response)
        self.assertEqual(response['status'], 'OK')

class FundraiserTests(TestCase):
    """
    Tests for fundraisers
    """
    fixtures = ['tests.json']

    def test_create(self):
        pass

    def test_transact(self):
        pass
