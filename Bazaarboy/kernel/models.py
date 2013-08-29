"""
All the core models for Bazaarboy
"""

import hashlib
import os
from django.db import models, IntegrityError
from django.db.models import F
from django.utils import timezone

class User(models.Model):
    """
    User model

    User is a real user of the site. It can make purchases on the site,
    as well as create profiles to in turn organize events.
    """
    full_name = models.CharField(max_length = 50)
    phone = models.CharField(max_length = 10)
    email = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 128, null = True, default = None)
    salt = models.CharField(max_length = 128, null = True, default = None)
    fb_id = models.CharField(max_length = 50, unique = True, 
                            null = True, default = None)
    fb_access_token = models.TextField(null = True, default = None)
    city = models.ForeignKey('City', null = True, default = None)
    following = models.ManyToManyField('Community', 
                                       through = 'User_following')
    points = models.IntegerField(default = 0)
    is_confirmed = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    # A copy of the user's original password
    __original_password = None

    def __init__(self, *args, **kwargs):
        """
        Overrides instantiation to keep track of password changes
        """
        super(User, self).__init__(*args, **kwargs)
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

class Wepay_account(models.Model):
    """
    A model to hold information for a wepay account
    """
    owner = models.ForeignKey('User')
    user_id = models.CharField(max_length = 50)
    account_id = models.CharField(max_length = 50)
    access_token = models.CharField(max_length = 80)
    name = models.CharField(max_length = 50)
    is_expired = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Wepay_checkout(models.Model):
    """
    A model for checkouts
    """
    payer = models.ForeignKey('User')
    payee = models.ForeignKey('Wepay_account')
    checkout_id = models.CharField(max_length = 50)
    amount = models.FloatField()
    description = models.CharField(max_length = 127)
    is_captured = models.BooleanField(default = False)
    is_refunded = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class City(models.Model):
    """
    City model

    City is the highest organizational structure. It groups communities
    together. Each city has a pseudo community that represents the city
    itself.
    """
    name = models.CharField(max_length = 50)
    state = models.CharField(max_length = 2)
    latitude = models.FloatField()
    longitude = models.FloatField()
    # Pseudo set to be nullable for the convenience of auto-creation
    pseudo = models.OneToOneField('Community', 
                                   related_name = 'pseudo_community',
                                   null = True, default = None)

    def save(self, *args, **kwargs):
        """
        Overrides save method to auto-create the city's pseudo community
        """
        if self.pk is None:
            # City is new, so let's create its pseudo community
            super(City, self).save(*args, **kwargs)
            pseudoCommunity = Community(name = self.name, city = self,
                                        latitude = self.latitude,
                                        longitude = self.longitude)
            pseudoCommunity.save()
            self.pseudo = pseudoCommunity
        super(City, self).save(*args, **kwargs)

class Community(models.Model):
    """ 
    Community model

    Community is the secondary organization structure. Residing under cities, 
    they can be neighborhoods, business districts, college campuses, and so 
    on. Each city has a pseudo community that represents the city itself.

    For example:

    Saint Louis (City)
        - Saint Louis (Community)
        - Central West End (Community)
        - Washington University in St. Louis (Community)
        - The Loop Business District (Community)
    """
    name = models.CharField(max_length = 50)
    description = models.TextField()
    city = models.ForeignKey('City')
    latitude = models.FloatField()
    longitude = models.FloatField()

class User_following(models.Model):
    """
    Community-User relation
    """
    user = models.ForeignKey('User')
    community = models.ForeignKey('Community')
    rank = models.IntegerField()

class Profile(models.Model):
    """
    Profile model

    Profile is the event creator. It represents event organizing entities in 
    communities like an event promotion agency (Top Shelf Entertainment), a 
    charity foundation (Linus Foundation), or a small business (Blueberry Hill).

    Each profile resides under a community. Users create and manage profiles. 
    A user can manage multiple profiles, and a profile can have multiple 
    managers.
    """
    name = models.CharField(max_length = 100)
    description = models.TextField()
    image = models.ForeignKey('Image', 
                              related_name = '%(class)s_image', 
                              null = True, default = None, 
                              on_delete = models.SET_NULL)
    cover = models.ForeignKey('Image', 
                              related_name = '%(class)s_cover', 
                              null = True, default = None, 
                              on_delete = models.SET_NULL)
    community = models.ForeignKey('Community')
    city = models.ForeignKey('City')
    category = models.CharField(max_length = 30)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    wepay_account = models.ForeignKey('Wepay_account', null = True, 
                                      default = None)
    managers = models.ManyToManyField('User', through = 'Profile_manager')
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to auto-set city
        """
        if self.pk is None:
            # Auto-set city for the new profile
            self.city = self.community.city
        super(Profile, self).save(*args, **kwargs)

class Profile_manager(models.Model):
    """
    Profile-User relation

    It denotes whether the manager is the creator of the profile.
    """
    user = models.ForeignKey('User')
    profile = models.ForeignKey('Profile')
    is_creator = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Event_base(models.Model):
    """
    A base model for information shared by the two types of events
    """
    name = models.CharField(max_length = 50)
    description = models.TextField()
    summary = models.CharField(max_length = 100)
    tags = models.CharField(max_length = 50)
    cover = models.ForeignKey('Image', 
                              related_name = '%(class)s_image', 
                              null = True, default = None, 
                              on_delete = models.SET_NULL)
    location = models.CharField(max_length = 100)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    is_private = models.BooleanField(default = False)
    is_launched = models.BooleanField(default = False)
    is_closed = models.BooleanField(default = False)
    category = models.CharField(max_length = 30)
    community = models.ForeignKey('Community', 
                                  related_name = '%(class)s_community', 
                                  null = True, default = None)
    city = models.ForeignKey('City', related_name = '%(class)s_city', 
                             null = True, default = None)
    access_token = models.CharField(max_length = 32, null = True, 
                                    default = None)
    created_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

class InsufficientQuantity(Exception):
    """
    An exception when the remaining quantity is not enough
    """
    pass

class Event(Event_base):
    """
    Model for normal events
    """
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null = True, default = None)
    organizers = models.ManyToManyField('Profile', 
                                        through = 'Event_organizer')

class Event_organizer(models.Model):
    """
    Organizer model for an event
    """
    event = models.ForeignKey('Event')
    profile = models.ForeignKey('Profile')
    is_creator = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Ticket(models.Model):
    """
    Ticket model for normal events
    """
    event = models.ForeignKey('Event')
    name = models.CharField(max_length = 15)
    description = models.CharField(max_length = 150)
    price = models.FloatField()
    quantity = models.IntegerField(null = True, default = None)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        """
        Overrides save to set up proper start/end time
        """
        if self.start_time is None:
            self.start_time = timezone.now()
        if self.end_time is None:
            self.end_time = self.event.start_time
        super(Ticket, self).save(*args, **kwargs)

class Purchase(models.Model):
    """
    Purchase model for a ticket
    """
    owner = models.ForeignKey('User')
    ticket = models.ForeignKey('Ticket')
    event = models.ForeignKey('Event')
    price = models.FloatField()
    checkout = models.ForeignKey('Wepay_checkout', null = True, default = None)
    is_expired = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Fundraiser(Event_base):
    """
    Event model for fundraisers
    """
    goal = models.FloatField()
    deadline = models.DateTimeField()
    organizers = models.ManyToManyField('Profile', 
                                        through = 'Fundraiser_organizer')

    def save(self, *args, **kwargs):
        """
        Overrides save method to auto-create a reward of no price
        """
        shouldCreateFreeReward = self.pk is None
        super(Fundraiser, self).save(*args, **kwargs)
        if shouldCreateFreeReward:
            reward = Reward(fundraiser = self, name = '', 
                            description = '', price = 0)
            reward.save()

class Fundraiser_organizer(models.Model):
    """
    Organizer model for a fundraiser
    """
    fundraiser = models.ForeignKey('Fundraiser')
    profile = models.ForeignKey('Profile')
    is_creator = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Reward(models.Model):
    """
    Reward model for fundraisers
    """
    fundraiser = models.ForeignKey('Fundraiser')
    name = models.CharField(max_length = 15)
    description = models.CharField(max_length = 150)
    price = models.FloatField()
    quantity = models.IntegerField(null = True, default = None)

class Donation(models.Model):
    """
    Donation model for a fundraiser
    """
    owner = models.ForeignKey('User')
    reward = models.ForeignKey('Reward')
    fundraiser = models.ForeignKey('Fundraiser')
    amount = models.FloatField()
    checkout = models.ForeignKey('Wepay_checkout')
    is_expired = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

class Criteria(models.Model):
    """
    Criteria model for sponsorship
    """
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 150)
    price = models.FloatField()
    quantity = models.IntegerField(null = True, default = None)

    class Meta:
        abstract = True

class Event_criteria(Criteria):
    """
    Sponsorship criteria model for an event
    """
    _for = models.ForeignKey('Event')

class Fundraiser_criteria(Criteria):
    """
    Sponsorship criteria model for a fundraiser
    """
    _for = models.ForeignKey('Fundraiser')

class Sponsorship(models.Model):
    """
    Sponsorship model
    """
    owner = models.ForeignKey('Profile', related_name = '%(class)s_profile')
    amount = models.FloatField()
    checkout_id = models.CharField(max_length = 50)
    is_captured = models.BooleanField(default = False)
    is_refunded = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

class Event_sponsorship(Sponsorship):
    """
    Sponsorship model for an event
    """
    criteria = models.ForeignKey('Event_criteria')
    _for = models.ForeignKey('Event')

class Fundraiser_sponsorship(Sponsorship):
    """
    Sponsorship model for a fundraiser
    """
    criteria = models.ForeignKey('Fundraiser_criteria')
    _for = models.ForeignKey('Fundraiser')

class Sponsorship_display(models.Model):
    """
    Sponsorship display model, which allows for custom sponsors
    """
    name = models.CharField(max_length = 50, null = True, default = None)
    description = models.CharField(max_length = 150, null = True, 
                                   default = None)
    image = models.ForeignKey('Image', null = True, default = None)
    sponsor = models.ForeignKey('Profile', null = True, default = None)

    class Meta:
        abstract = True

class Event_sponsorship_display(Sponsorship_display):
    """
    Event sponsorship display
    """
    sponsorship = models.ForeignKey('Event_sponsorship', 
                                    null = True, default = None)
    _for = models.ForeignKey('Event')

class Fundraiser_sponsorship_display(Sponsorship_display):
    """
    Fundraiser sponsorship display
    """
    sponsorship = models.ForeignKey('Fundraiser_sponsorship', 
                                    null = True, default = None)
    _for = models.ForeignKey('Fundraiser')

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