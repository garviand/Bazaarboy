import os
import hashlib
from django.db import models

class Admin(models.Model):
    """
    Admin user model
    """
    name = models.CharField(max_length = 15, unique = True)
    password = models.CharField(max_length = 128)
    salt = models.CharField(max_length = 128)
    ADMIN_ROLES = (
        ('B', 'Basic'),
        ('S', 'Super')
    )
    role = models.CharField(max_length = 1, choices = ADMIN_ROLES, 
                            default = 'B')

    # A copy of the user's original password
    __original_password = None

    def __init__(self, *args, **kwargs):
        """
        Overrides instantiation to keep track of password changes
        """
        super(Admin, self).__init__(*args, **kwargs)
        # Save a copy of the original password
        self.__original_password = self.password

    def save(self, *args, **kwargs):
        """
        Overrides save method to rehash password
        """
        if (self.password is not None and 
            (self.pk is None or self.password != self.__original_password)):
            # Password is changed, rehash it
            self.salt = os.urandom(128).encode('base_64')[:128]
            saltedPassword = self.salt + self.password
            # Hash the password with salt
            self.password = hashlib.sha512(saltedPassword).hexdigest()
        super(Admin, self).save(*args, **kwargs)
        self.__original_password = self.password