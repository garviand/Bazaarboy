"""
Controller for sponsorships
"""

import cgi
from django.utils import timezone
from kernel.models import *
from src.controllers.request import *
from src.serializer import serialize_one