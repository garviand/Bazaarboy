from django.db import models

class User(models.Model):
    """
    User model

    User is a real user of the site. It can make purchases on the site,
    as well as create profiles to in turn organize events.
    """
    email = models.CharField(
        max_length = 50, unique = True, 
        null = True, default = None
    )
    password = models.CharField(max_length = 128, null = True, default = None)
    fbid = models.CharField(
        max_length = 50, unique = True, 
        null = True, default = None
    )
    created_time = models.DateTimeField(auto_now_add = True)

    def save(self, *args, **kwargs):
        """
        Overrides the save method so that:
        1. If a new password is set, it will be hashed.
        2. User can either have a fbid or have both email and password
        """
        if self.fbid is None and (self.email is None or self.password is None):
            return False
        if self.password is not None and len(self.password) < 128:
            # Hash the password
            pass
        return super(User, self).save(*args, **kwargs)

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
    pseudo = models.OneToOneField('Community')

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
    city = models.ForeignKey('City', related_name = 'Community')
    latitude = models.FloatField()
    longitude = models.FloatField()

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
    community = models.ForeignKey('Community', related_name = 'Profile')
    category = models.CharField(max_length = 30)
    latitude = models.FloatField(null = True, default = None)
    longitude = models.FloatField(null = True, default = None)
    managers = models.ManyToManyField('User', through = 'Profile_manager')
    created_time = models.DateTimeField(auto_now_add = True)

class Profile_manager(models.Model):
    """
    Profile-User relation

    It denotes whether the manager is the creator of the profile.
    """
    user = models.ForeignKey('User')
    profile = models.ForeignKey('Profile')
    creator = models.BooleanField(default = False)

class Event(models.Model):
    """
    Event model
    """
    pass