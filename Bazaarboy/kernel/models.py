"""
All the core models for Bazaarboy
"""

import hashlib
import os
import random
import string
import uuid
from django.db import models
from django.db.models import Q, Sum, Count
from django.utils import timezone
from palette import Color

import pdb

class User(models.Model):
    """
    User model

    User is a real user of the site. It can make purchases on the site,
    as well as create profiles to in turn organize events.
    """
    email = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 128, null = True, default = None)
    salt = models.CharField(max_length = 128, null = True, default = None)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 10)
    is_confirmed = models.BooleanField(default = False)
    is_active = models.BooleanField(default = True)
    created_time = models.DateTimeField(auto_now_add = True)

    full_name = None
    # A copy of the user's original password
    __original_password = None

    def __init__(self, *args, **kwargs):
        """
        Overrides instantiation to keep track of password changes
        """
        super(User, self).__init__(*args, **kwargs)
        if self.pk is not None:
            self.full_name = self.first_name + ' ' + self.last_name
        # Save a copy of the original password
        self.__original_password = self.password

    def save(self, *args, **kwargs):
        """
        Overrides save method to rehash password if necessary
        """
        if ((self.pk is None or self.password != self.__original_password) and 
            self.password is not None):
            # Password is changed, rehash it
            self.salt = os.urandom(128).encode('base_64')[:128]
            saltedPassword = self.salt + self.password
            # Hash the password with salt
            self.password = hashlib.sha512(saltedPassword).hexdigest()
        super(User, self).save(*args, **kwargs)
        self.__original_password = self.password

class User_confirmation_code(models.Model):
    """
    A code used to confirm a user's email address
    """
    user = models.OneToOneField('User')
    code = models.CharField(max_length = 128)

class User_reset_code(models.Model):
    """
    A code used to reset a user's password
    """
    user = models.ForeignKey('User')
    code = models.CharField(max_length = 128)
    is_expired = models.BooleanField(default = False)
    expiration_time = models.DateTimeField()

class Payment_account(models.Model):
    """
    A model to hold information for a payment account
    """
    owner = models.ForeignKey('User')
    user_id = models.CharField(max_length = 255)
    refresh_token = models.CharField(max_length = 255)
    access_token = models.CharField(max_length = 255)
    publishable_key = models.CharField(max_length = 255)
    created_time = models.DateTimeField(auto_now_add = True)

class Subscription(models.Model):
    """
    A model to hold information about a Stripe subscription
    """
    owner = models.ForeignKey('Profile')
    customer_id = models.CharField(max_length = 255)
    subscription_id = models.CharField(max_length = 255)
    plan_id = models.CharField(max_length = 255)
    is_active = models.BooleanField(default = True)
    credits = models.IntegerField(default = 0)
    created_time = models.DateTimeField(auto_now_add = True)
    

class Checkout(models.Model):
    """
    A model for checkouts
    """
    payer = models.ForeignKey('User')
    payee = models.ForeignKey('Payment_account')
    checkout_id = models.CharField(max_length = 255)
    amount = models.IntegerField() # in cents
    description = models.CharField(max_length = 127)
    is_charged = models.BooleanField(default = False)
    is_refunded = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Profile(models.Model):
    """
    Profile model

    Profile is the event creator. It represents event organizing entities in 
    communities like an event promotion agency (Top Shelf Entertainment), a 
    charity foundation (Linus Foundation), or a small business (Blueberry Hill).

    A user can manage multiple profiles, and a profile can have multiple 
    managers.
    """
    name = models.CharField(max_length = 100)
    description = models.TextField()
    image = models.ForeignKey('Image', 
                              related_name = '%(class)s_image', 
                              null = True, default = None, 
                              on_delete = models.SET_NULL)
    location = models.CharField(max_length = 100)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    email = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 10, null = True, default = None)
    link_website = models.CharField(max_length = 1024, null = True, 
                                    default = None)
    link_facebook = models.CharField(max_length = 1024, null = True, 
                                     default = None)
    EIN = models.CharField(max_length = 10, null = True, default = None)
    is_non_profit = models.BooleanField(default = False)
    is_verified = models.BooleanField(default = False)
    payment_account = models.ForeignKey('Payment_account', 
                                        null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)
    managers = models.ManyToManyField('User', through = 'Profile_manager')

class Channel(models.Model):
    """
    Profile channel model
    """
    profile = models.ForeignKey('Profile')
    subscribe_list = models.ForeignKey('List', null = True, default = None)
    cover = models.ForeignKey('Image', null = True, default = None)
    tagline = models.CharField(max_length = 250, null = True, default = None)
    hashtag = models.CharField(max_length = 250, null = True, default = None)
    active = models.BooleanField(default = False)
    slug = models.CharField(max_length = 30, null = True, default = None, unique = True)
    created_time = models.DateTimeField(auto_now_add = True)

class Profile_manager(models.Model):
    """
    Profile-User relation

    It denotes whether the manager is the creator of the profile.
    """
    user = models.ForeignKey('User')
    profile = models.ForeignKey('Profile')
    is_creator = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Event(models.Model):
    """
    Event model
    """
    name = models.CharField(max_length = 150)
    summary = models.CharField(max_length = 250)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null = True, default = None)
    location = models.CharField(max_length = 100)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    cover = models.ForeignKey('Image', 
                              related_name = '%(class)s_image', 
                              null = True, default = None, 
                              on_delete = models.SET_NULL)
    tags = models.CharField(max_length = 50)
    category = models.CharField(max_length = 30)
    color = models.CharField(max_length = 30, default="#FAA638")
    premium = models.BooleanField(default = False)
    is_launched = models.BooleanField(default = False)
    launched_time = models.DateTimeField(null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)
    organizers = models.ManyToManyField('Profile', 
                                        related_name = '%(class)s_organizer', 
                                        through = 'Organizer')
    sponsors = models.ManyToManyField('Profile', 
                                      related_name = '%(class)s_sponsorship', 
                                      through = 'Sponsorship')
    slug = models.CharField(max_length = 30, null = True, default = None, unique = True)
    is_deleted = models.BooleanField(default = False)

    def totalRSVP(self):
        stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = self)
        return stats.aggregate(Count('items'))['items__count']

    def totalRevenue(self):
        stats = Purchase.objects.filter(Q(checkout = None) | 
                                        Q(checkout__is_charged = True, 
                                          checkout__is_refunded = False), 
                                        event = self)
        if stats.aggregate(Sum('amount'))['amount__sum'] is None:
            return 0
        else:
            return stats.aggregate(Sum('amount'))['amount__sum']

    def color_test(self):
        try:
            c = Color(self.color)
        except ValueError:
            return True
        if c.w3_contrast_ratio(Color("#4a4a4a")) < 5:
            return False
        return True

    def color_dark(self):
        try:
            c = Color(self.color)
        except ValueError:
            return self.color
        return c.darker(amt=0.1).css

    def color_light(self):
        try:
            c = Color(self.color)
        except ValueError:
            return self.color
        return c.lighter(amt=0.1).css

    def color_translucent(self):
        try:
            c = Color(self.color, a=.25)
        except ValueError:
            return self.color
        return c.css

def randomConfirmationCode(size=6):
    """
    A method for generating confirmation code like 6ABX78
    """
    charSet = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(charSet) for x in range(size))
    return code

class Organizer(models.Model):
    """
    Organizer model for an event
    """
    event = models.ForeignKey('Event')
    profile = models.ForeignKey('Profile')
    is_creator = models.BooleanField(default = False)
    is_public = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Collaboration_request(models.Model):
    """
    Add Organizer to Event Request model
    """
    event = models.ForeignKey('Event')
    sender = models.ForeignKey('Organizer')
    profile = models.ForeignKey('Profile', null = True, default = None)
    user = models.ForeignKey('User', null = True, default = None) # Used to capture request before needing to go through profile creation
    email = models.CharField(max_length = 100, null = True, default = None)
    code = models.CharField(max_length = 30)
    accepted = models.DateTimeField(null = True, default = None)
    is_rejected = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to generate confirmation code
        """
        if self.pk is None:
            self.code = randomConfirmationCode(30)
        super(Collaboration_request, self).save(*args, **kwargs)

class Ticket(models.Model):
    """
    Ticket model for events
    """
    event = models.ForeignKey('Event')
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 400)
    price = models.FloatField()
    quantity = models.IntegerField(null = True, default = None)
    start_time = models.DateTimeField(null = True, default = None)
    end_time = models.DateTimeField(null = True, default = None)
    request_address = models.BooleanField(default = False)
    extra_fields = models.TextField()
    attachment = models.FileField(upload_to = 'uploads/attachment/%Y-%m-%d', null = True, default = None)
    is_deleted = models.BooleanField(default = False)
    order = models.IntegerField(null = False, default = 0)

class Promo(models.Model):
    """
    Promo code model
    """
    event = models.ForeignKey('Event')
    tickets = models.ManyToManyField('Ticket')
    code = models.CharField(max_length = 20)
    amount = models.IntegerField(null = True, default = None)
    discount = models.FloatField(null = True, default = None)
    email_domain = models.CharField(max_length = 20)
    quantity = models.IntegerField(null = True, default = None)
    start_time = models.DateTimeField(null = True, default = None)
    expiration_time = models.DateTimeField(null = True, default = None)
    is_deleted = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Invite(models.Model):
    """
    Invite model
    """
    profile = models.ForeignKey('Profile')
    event = models.ForeignKey('Event')
    lists = models.ManyToManyField('List')
    image = models.ForeignKey('Image', null = True, default = None)
    color = models.CharField(max_length = 50, default="#FAA638")
    message = models.CharField(max_length = 5000, null = True, default = None)
    details = models.CharField(max_length = 1000, null = True, default = None)
    salutation = models.CharField(max_length = 100, null = True, default = None)
    salutation_name = models.CharField(max_length = 100, null = True, default = None)
    paid = models.BooleanField(default = False)
    price = models.IntegerField(default = 0)
    is_sent = models.BooleanField(default = False)
    sent_at = models.DateTimeField(null = True, default = None)
    recipients = models.IntegerField(null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)
    is_deleted = models.BooleanField(default = False)

class Invite_stat(models.Model):
    """
    Invite Statistic
    """
    email_id = models.CharField(max_length = 100, unique = True)
    to = models.CharField(max_length = 150, null = True, default = None)
    invite = models.ForeignKey('Invite', null = True, default = None)
    event = models.ForeignKey('Event', null = True, default = None)
    profile = models.ForeignKey('Profile', null = True, default = None)
    clicks = models.IntegerField(null = True, default = None)
    opens = models.IntegerField(null = True, default = None)
    city = models.CharField(max_length = 100, null = True, default = None)
    zip_code = models.CharField(max_length = 20, null = True, default = None)

class Recap(models.Model):
    """
    Recap model - Post event actions including adding attendees to list and sending follow up email
    """
    organizer = models.OneToOneField('Organizer')
    is_viewed = models.BooleanField(default = False)
    list_added = models.BooleanField(default = False)
    email_id = models.CharField(max_length = 150, null = True, default = None)

class Follow_up(models.Model):
    """
    Follow up model
    """
    recap = models.ForeignKey('Recap')
    image = models.ForeignKey('Image', null = True, default = None)
    tickets = models.ManyToManyField('Ticket')
    color = models.CharField(max_length = 50, default="#FAA638")
    heading = models.CharField(max_length = 1000, null = True, default = None)
    message = models.CharField(max_length = 5000, null = True, default = None)
    paid = models.BooleanField(default = False)
    price = models.IntegerField(default = 0)
    button_text = models.CharField(max_length = 100, null = True, default = None)
    button_target = models.CharField(max_length = 300, null = True, default = None)
    is_sent = models.BooleanField(default = False)
    sent_at = models.DateTimeField(null = True, default = None)
    recipients = models.IntegerField(null = True, default = None)
    attachment = models.ForeignKey('Pdf', null = True, default = None)
    email_id = models.CharField(max_length = 150, null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)
    is_deleted = models.BooleanField(default = False)

class Follow_up_stat(models.Model):
    """
    Follow Up Statistic
    """
    email_id = models.CharField(max_length = 100, unique = True)
    to = models.CharField(max_length = 150, null = True, default = None)
    follow_up = models.ForeignKey('Follow_up', null = True, default = None)
    event = models.ForeignKey('Event', null = True, default = None)
    profile = models.ForeignKey('Profile', null = True, default = None)
    clicks = models.IntegerField(null = True, default = None)
    opens = models.IntegerField(null = True, default = None)
    city = models.CharField(max_length = 100, null = True, default = None)
    zip_code = models.CharField(max_length = 20, null = True, default = None)

class Purchase(models.Model):
    """
    Purchase model for tickets
    """
    owner = models.ForeignKey('User')
    event = models.ForeignKey('Event')
    code = models.CharField(max_length = 6)
    items = models.ManyToManyField('Ticket', through = 'Purchase_item')
    promos = models.ManyToManyField('Promo')
    amount = models.FloatField(default = 0)
    checkout = models.ForeignKey('Checkout', null = True, default = None)
    invite = models.ForeignKey('Invite', null = True, default = None)
    is_expired = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to generate confirmation code
        """
        if self.pk is None:
            self.code = randomConfirmationCode()
        super(Purchase, self).save(*args, **kwargs)

class Purchase_item(models.Model):
    """
    A ticket item in a purchase
    """
    purchase = models.ForeignKey('Purchase')
    ticket = models.ForeignKey('Ticket')
    price = models.FloatField()
    address = models.TextField(null = True, default = None)
    extra_fields = models.TextField()
    is_checked_in = models.BooleanField(default = False)
    checked_in_time = models.DateTimeField(null = True, default = None)

class Purchase_promo(models.Model):
    """
    Relationship model for purchase and promo code
    """
    purchase = models.ForeignKey('Purchase')
    promo = models.ForeignKey('Promo')
    quantity = models.IntegerField(default = 1)

class Criteria(models.Model):
    """
    Criteria model for sponsorship
    """
    event = models.ForeignKey('Event')
    name = models.CharField(max_length = 50)
    description = models.TextField()
    price_lower = models.FloatField(null = True, default = None)
    price_upper = models.FloatField(null = True, default = None)
    quantity = models.IntegerField(null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)

class Sponsorship(models.Model):
    """
    Sponsorship model
    """
    owner = models.ForeignKey('Profile', null = True, default = None)
    event = models.ForeignKey('Event')
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500)
    image = models.ForeignKey('Image', null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)

class Reward(models.Model):
    """
    Reward model
    """
    creator = models.ForeignKey('Profile')
    name = models.CharField(max_length = 150)
    description = models.CharField(max_length = 350)
    value = models.FloatField()
    extra_fields = models.TextField(default = '{}')
    attachment = models.ForeignKey('Pdf', null = True, default = None, on_delete = models.SET_NULL)
    is_deleted = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Reward_item(models.Model):
    """
    Reward item model
    """
    reward = models.ForeignKey('Reward')
    owner = models.ForeignKey('Profile')
    quantity = models.IntegerField()
    expiration_time = models.DateTimeField()
    created_time = models.DateTimeField(auto_now_add = True)

class Claim(models.Model):
    """
    Claim for a reward
    """
    email = models.CharField(max_length = 100)
    owner = models.ForeignKey('User', null = True, default = None)
    item = models.ForeignKey('Reward_item')
    code = models.CharField(max_length = 30)
    token = models.CharField(max_length = 128)
    extra_fields = models.TextField(default = '{}')
    is_claimed = models.BooleanField(default = False)
    claimed_time = models.DateTimeField(null = True, default = None)
    is_redeemed = models.BooleanField(default = False)
    redemption_time = models.DateTimeField(null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Override save to generate token at creation
        """
        if self.pk is None:
            self.token = uuid.uuid4().hex
        if self.pk is None:
            self.code = randomConfirmationCode()
        super(Claim, self).save(*args, **kwargs)

class List(models.Model):
    """
    Contact list model
    """
    owner = models.ForeignKey('Profile')
    name = models.CharField(max_length = 50)
    is_hidden = models.BooleanField(default = True)
    is_deleted = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class List_item(models.Model):
    """
    Item in a contact list
    """
    _list = models.ForeignKey('List')
    email = models.CharField(max_length = 50)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    note = models.TextField()

class Sign_up(models.Model):
    """
    Sign Up Form
    """
    owner = models.ForeignKey('Profile')
    name = models.CharField(max_length = 100)
    description = models.CharField(max_length = 500)
    image = models.ForeignKey('Image', null = True, default = None)
    start_time = models.DateTimeField(null = True, default = None)
    end_time = models.DateTimeField(null = True, default = None)
    extra_fields = models.TextField(default = '{}')
    created_time = models.DateTimeField(auto_now_add = True)

class Sign_up_item(models.Model):
    """
    Sign Up Member - Can belong to a Sign Up or just a Profile
    """
    sign_up = models.ForeignKey('Sign_up', null = True, default = None)
    profile = models.ForeignKey('Profile', null = True, default = None)
    email = models.CharField(max_length = 100)
    first_name = models.CharField(max_length = 100)
    last_name = models.CharField(max_length = 100)
    extra_fields = models.TextField(default = '{}')
    assigned = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)



class Unsubscribe(models.Model):
    """
    Unsubscribe from Invites and Follow-Ups
    """
    email = models.CharField(max_length = 100)
    profile = models.ForeignKey('Profile', null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)

class Image(models.Model):
    """
    Image model
    """
    source = models.ImageField(upload_to = 'uploads/%Y-%m-%d/')
    caption = models.CharField(max_length = 100)
    is_archived = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        """
        Automatically delete the image file after model deletion
        """
        self.source.delete(save = False)
        super(Image, self).delete(*args, **kwargs)

class Csv(models.Model):
    """
    CSV model
    """
    source = models.FileField(upload_to = 'uploads/csv/%Y-%m-%d/')
    is_archived = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        """
        Automatically delete the CSV file after model deletion
        """
        self.source.delete(save = False)
        super(Csv, self).delete(*args, **kwargs)

class Pdf(models.Model):
    """
    PDF model
    """
    source = models.FileField(upload_to = 'uploads/attachment/%Y-%m-%d/')
    name = models.CharField(max_length = 500)
    is_archived = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        """
        Automatically delete the PDF file after model deletion
        """
        self.source.delete(save = False)
        super(Pdf, self).delete(*args, **kwargs)
