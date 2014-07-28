"""
A collection of useful regular expressions
"""

import re

REGEX_EMAIL = re.compile(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.(([0-9]{1,3})|([a-zA-Z]{2,3})|(aero|coop|info|museum|name))$')
REGEX_NAME = re.compile(r"^[a-zA-Z,.' -]+$")
REGEX_URL = re.compile(r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
REGEX_EIN = re.compile(r'^[1-9]\d?-\d{7}$')
REGEX_SLUG = re.compile(r'^[A-Za-z0-9-]{1,30}$')