# -*- coding: utf-8 -*-
from django.dispatch import Signal, receiver

from mediastorage.signals import collecting_formats

from .models import FORMATS


get_transferable_models = Signal(providing_args=['sender', 'qry'])


@receiver(collecting_formats)
def deliver_formats(sender, *args, **kwargs):
    for entry in FORMATS:
        kwargs['format_list'].append((entry, FORMATS[entry]))
