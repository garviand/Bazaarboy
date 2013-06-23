from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from kernel.models import *

class Add_points_event(models.Model):
    """
    Triggerred when a user earns points by attending events
    """
    user = models.ForeignKey('kernel.User')
    # Use generic relations for two types of events
    event_type = models.ForeignKey(ContentType)
    event_id = models.PositiveIntegerField()
    event = generic.GenericForeignKey('event_type', 'event_id')
    points = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add = True)

class Subtract_points_event(models.Model):
    """
    Triggerred when a user loses points by redeeming a redeemable
    """
    user = models.ForeignKey('kernel.User')
    redeemable = models.ForeignKey('kernel.Redeemable')
    points = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add = True)