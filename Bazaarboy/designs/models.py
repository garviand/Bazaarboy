"""
Models for the Bazaarboy Designs app
"""

import hashlib
import os
import random
import string
from django.db import models
from django.utils import timezone
import kernel.models as kernel

import pdb

# Create your models here.



class Project(models.Model):
	"""
	Project model
	"""
	owner = models.ForeignKey(kernel.User, null = True, default = None)
	designer = models.ForeignKey('Designer', null = True)
	event = models.ForeignKey(kernel.Event, null = True, default = None)
	code = models.CharField(max_length = 15)
	description = models.TextField()
	services = models.ManyToManyField('Service')
	images = models.ManyToManyField('Asset', null = True)
	checkout = models.ForeignKey(kernel.Checkout, null = True, default = None)
	is_completed = models.BooleanField(default = False)
	created_time = models.DateTimeField(auto_now_add = True)

	def save(self, *args, **kwargs):
		"""
		Overrides save to generate confirmation code
		"""
		if self.pk is None:
			self.code = randomProjectCode()
		super(Project, self).save(*args, **kwargs)

def randomProjectCode(size=15):
	"""
	A method for generating project code
	"""
	charSet = string.ascii_uppercase + string.digits
	code = ''.join(random.choice(charSet) for x in range(size))
	return code

class Service(models.Model):
	"""
	Service model
	"""
	name = models.CharField(max_length = 150)
	description = models.CharField(max_length = 350)
	image = models.ForeignKey('Asset', null = True, default = None)
	price = models.FloatField()

class Submission(models.Model):
	"""
	Submission model
	"""
	project = models.ForeignKey('Project')
	service = models.ForeignKey('Service')
	images = models.ManyToManyField('Asset')
	notes = models.TextField()
	is_finalized = models.BooleanField(default = False)
	created_time = models.DateTimeField(auto_now_add = True)

class Asset(models.Model):
    """
    Asset model
    """
    source = models.FileField(upload_to = 'uploads/designs/%Y-%m-%d/')
    is_archived = models.BooleanField(default = False)
    created_time = models.DateTimeField(auto_now_add = True)

    def delete(self, *args, **kwargs):
        """
        Automatically delete the Asset file after model deletion
        """
        self.source.delete(save = False)
        super(Csv, self).delete(*args, **kwargs)

    def is_image(self):
    	image_filetypes = ['.jpg', '.png', '.gif']
        name, extension = os.path.splitext(self.source.name)
        return extension.lower() in image_filetypes

    def shortName(self):
    	return self.source.name.split("/")[-1]

class Designer(models.Model):
    """
    Designer model

    Designer is a the designer assigned to each project.
    """
    email = models.CharField(max_length = 50, unique = True)
    password = models.CharField(max_length = 128, null = True, default = None)
    salt = models.CharField(max_length = 128, null = True, default = None)
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    created_time = models.DateTimeField(auto_now_add = True)

    # A copy of the user's original password
    __original_password = None

    def __init__(self, *args, **kwargs):
        """
        Overrides instantiation to keep track of password changes
        """
        super(Designer, self).__init__(*args, **kwargs)
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
        super(Designer, self).save(*args, **kwargs)
        self.__original_password = self.password