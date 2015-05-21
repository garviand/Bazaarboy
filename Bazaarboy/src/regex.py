"""
A collection of useful regular expressions
"""

import re

REGEX_EMAIL = re.compile(r'^[\.\w]{1,}[@]\w+[.]\w+')
REGEX_NAME = re.compile(r"^[a-zA-Z,.' -]+$")
REGEX_URL = re.compile(r'((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)')
REGEX_EIN = re.compile(r'^[1-9]\d?-\d{7}$')
REGEX_SLUG = re.compile(r'^[A-Za-z0-9-]{1,30}$')
REGEX_HEX_COLOR = re.compile(r'^#([0-9a-f]{3}){1,2}$')