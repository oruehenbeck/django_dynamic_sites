# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured


def ret_contenttypes(*args, **kwargs):
    """
    Takes a blacklist or a whitelist of model names
    and returns queryset of ContentTypes
    """
    if not 'app_label' in kwargs.keys():
        raise ImproperlyConfigured('Missing app_label')
    app_label = kwargs['app_label']
    whitelist = kwargs['whitelist'] if 'whitelist' in kwargs.keys() else None
    blacklist = kwargs['blacklist'] if 'blacklist' in kwargs.keys() else None

    if whitelist and blacklist:
        raise ImproperlyConfigured("Dont configure kwargs['blacklist'] and kwargs['whitelist']")

    if blacklist:
        return ContentType.objects.filter(app_label=app_label).exclude(model__in=blacklist)

    if whitelist:
        tmp_whitelist = ContentType.objects.none()
        for name in whitelist:
            tmp_whitelist = tmp_whitelist | ContentType.objects.filter(app_label=app_label, model=name)

        return tmp_whitelist

    return ContentType.objects.filter(app_label=app_label)
