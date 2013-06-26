"""
All the core models for Bazaarboy
"""

import os
import hashlib
from django.db import models, IntegrityError
from django.db.models import F
from django.utils import timezone

class User(models.Model):
    """
    User model

    User is a real user of the site. It can make purchases on the site,
    as well as create profiles to in turn organize events.
    """
    email = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 128)
    salt = models.CharField(max_length = 128)
    city = models.ForeignKey('City')
    following = models.ManyToManyField('Community', 
                                       through = 'User_following')
    points = models.IntegerField()
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
        Overrides save method to validate the model and rehash password
        """
        if self.pk is None:
            self.points = 0
        if self.pk is None or self.password != self.__original_password:
            # Password is changed, rehash it
            self.salt = os.urandom(128).encode('base_64')[:128]
            saltedPassword = self.salt + self.password
            # Hash the password with salt
            self.password = hashlib.sha512(saltedPassword).hexdigest()
        super(User, self).save(*args, **kwargs)
        self.__original_password = self.password

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
    name = models.CharField(max_length = 100)
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
    name = models.CharField(max_length = 100)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null = True, default = None)
    location = models.CharField(max_length = 100)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    is_private = models.BooleanField(default = False)
    is_launched = models.BooleanField(default = False)
    is_closed = models.BooleanField(default = False)
    category = models.CharField(max_length = 30)
    owner = models.ForeignKey('Profile')
    community = models.ForeignKey('Community', 
                                  related_name = '%(class)s_community')
    city = models.ForeignKey('City', related_name = '%(class)s_city')
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to auto-set community and city
        """
        if self.pk is None:
            # Auto-set the community and city for the new event
            self.community = self.owner.community
            self.city = self.owner.city
        super(self.__class__, self).save(*args, **kwargs)

class InsufficientQuantity(Exception):
    """
    An exception when the remaining quantity is not enough
    """
    pass

class Event(Event_base):
    """
    Event model for normal events
    """
    pass

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
    price = models.FloatField()
    created_time = models.DateTimeField(auto_now_add = True)

class Initiative(Event_base):
    """
    Event model for initiative-based events
    """
    goal = models.FloatField()
    deadline = models.DateTimeField()
    is_reached = models.BooleanField(default = False)

class Reward(models.Model):
    """
    Reward model for initiative events
    """
    initiative = models.ForeignKey('Initiative')
    name = models.CharField(max_length = 15)
    description = models.CharField(max_length = 150)
    price = models.FloatField()
    quantity = models.IntegerField(null = True, default = None)

class Pledge(models.Model):
    """
    Pledge model for a reward
    """
    owner = models.ForeignKey('User')
    reward = models.ForeignKey('Reward')
    amount = models.FloatField()
    created_time = models.DateTimeField(auto_now_add = True)

class Fundraiser(Event_base):
    """
    Event model for fundraising events
    """
    pass

    def save(self, *args, **kwargs):
        """
        Overrides save to force an end time for the fundraiser
        """
        if self.end_time is None:
            raise IntegrityError()
        super(Fundraiser, self).save(*args, **kwargs)

class Donation(models.Model):
    """
    Donation model for a fundraiser
    """
    owner = models.ForeignKey('User')
    fundraiser = models.ForeignKey('Fundraiser')
    amount = models.FloatField()
    created_time = models.DateTimeField(auto_now_add = True)

class Redeemable(models.Model):
    """
    Redeemable rewards for points
    """
    owner = models.ForeignKey('Profile')
    name = models.CharField(max_length = 50)
    description = models.CharField(max_length = 500)
    quantity = models.IntegerField(null = True)
    value = models.IntegerField() # Monetary value
    points = models.IntegerField()
    is_expired = models.BooleanField(default = False)
    expiration_time = models.DateTimeField(null = True, default = None)
    community = models.ForeignKey('Community')
    city = models.ForeignKey('City')
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to auto-set community and city
        """
        if self.pk is None:
            # Auto-set the community and city for the redeemable
            self.community = self.owner.community
            self.city = self.owner.city
        super(Redeemable, self).save(*args, **kwargs)

class InsufficientPoints(Exception):
    """
    An exception for when points are not sufficient to claim a redeemable
    """
    def __init__(self, pointsNeeded):
        self.pointsNeeded = pointsNeeded

class ExpiredRedeemable(Exception):
    """
    An exception for claiming an expired redeemable
    """
    def __init__(self, redeemable):
        self.redeemable = redeemable

class Claim(models.Model):
    """
    A claim for a redeemable
    """
    redeemable = models.ForeignKey('Redeemable')
    owner = models.ForeignKey('User')
    code = models.CharField(max_length = 100)
    is_redeemed = models.BooleanField(default = False)
    redeemed_time = models.DateTimeField(null = True, default = None)
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides save to conduct proper claiming behavior
        """
        shouldFireSubtractEvent = False
        if self.pk is None:
            # Check if the redeemable is expired
            if (self.redeemable.is_expired or 
                self.redeemable.expiration_time <= timezone.now()):
                raise ExpiredRedeemable(self.redeemable)
            # Check if the redeemable has sufficient quantity
            if (self.redeemable.quantity is not None and 
                self.redeemable.quantity < 1):
                raise InsufficientQuantity()
            # Check if user has sufficient points
            remainingPoints = self.owner.points - self.redeemable.points
            if remainingPoints < 0:
                raise InsufficientPoints(abs(remainingPoints))
            # All checks passed, perform transactions
            self.redeemable.quantity = F('quantity') - 1
            self.redeemable.save()
            self.user.points = F('points') - self.redeemable.points
            self.user.save()
            shouldFireSubtractEvent = True
        super(Claim, self).save(*args, **kwargs)
        if shouldFireSubtractEvent:
            # Fire a subtract points event
            Subtract_points_event(user = self.owner, 
                                  redeemable = self.redeemable, 
                                  points = self.redeemable.points).save()