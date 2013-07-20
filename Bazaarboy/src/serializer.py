"""
A custom serializer for models
"""

from datetime import datetime
from django.utils.encoding import is_protected_type
from kernel.models import *

FORMAT_DATETIME = '%Y-%m-%d %X'

def serialize_one(obj, selectedFields=None):
    """
    Serialize a model object into a dictionary. The method is modified based 
    on Django's serializer, but omits many to many field support and changes 
    the DateTimeField output format.
    If selectedFields are specified, only the selected fields will be returned.
    """
    outputObj = {
        'pk':obj.pk
    }
    concreteModel = obj._meta.concrete_model
    for field in concreteModel._meta.local_fields:
        if field.serialize:
            if field.rel is None:
                # Normal field
                if (selectedFields is None or 
                    field.attname in selectedFields):
                    value = field._get_val_from_obj(obj)
                    if is_protected_type(value):
                        if isinstance(value, datetime):
                            value = value.strftime(FORMAT_DATETIME)
                        outputObj[field.name] = value
                    else:
                        outputObj[field.name] = field.value_to_string(obj)
            else:
                # Foreign Key
                if (selectedFields is None or 
                    field.attname[:-3] in selectedFields):
                    value = getattr(obj, field.name)
                    if hasattr(value, 'name'):
                        valueObj = {
                            'id':value.id,
                            'name':value.name
                        }
                        outputObj[field.name] = valueObj
                    elif value is not None:
                        outputObj[field.name] = value.id
                    else:
                        outputObj[field.name] = value
    return outputObj

def serialize(qs):
    """
    Serialize a whole QuerySet
    """
    outputs = []
    for obj in qs:
        outputs.append(serialize_one(obj))
    return outputs