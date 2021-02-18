# -*- coding: utf-8 -*-
from django.dispatch import Signal

from .models import FORMATS


get_transferable_models = Signal(providing_args=['sender', 'qry'])


# callback functions
def deliver_formats(sender, *args, **kwargs):
    for entry in FORMATS:
        kwargs['format_list'].append((entry, FORMATS[entry]))


## REGISTER
try:
    # import here to allow dynamic_sites to be used without the mediastorage app
    from mediastorage.signals import collecting_formats
    collecting_formats.connect(deliver_formats)
except:
    pass