# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
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
            tmp_whitelist |= ContentType.objects.filter(app_label=app_label, model=name)

        return tmp_whitelist

    return ContentType.objects.filter(app_label=app_label)


def generate_filterform_class(self, form=forms.Form, _fields=None, _excluded=None):
    """
    Return a Form which acts a filter for a given model.

    The model is found in self

    ''fields'' is an optional list of field names. If provided, include only the named fields.
    If omitted, use all fields.

    ''excluded'' optional, inversion of fields. If a field is in both fields and excluded,
    the field is excluded.
    """

    # Starting with generating a list of fields for which should be filtered by
    fields = []

    for field in self._meta.fields:
        if not _excluded is None and field in _excluded:
            continue
        if not _fields is None and field not in _fields:
            continue
        fields.append(field)

    # Now with the finalised fieldlist, the list of actual filterfields has to be generated
    filter_fields = {}
    searchbar = False

    for field in fields:
        if not searchbar and (isinstance(field, models.CharField) or isinstance(field, models.TextField) or isinstance(field, models.ManyToManyField)):
            filter_fields['searchbar'] = forms.CharField(label=_('Suchleiste'), max_length=100, widget=forms.TextInput(attrs={'placeholder': _('Suchen')}), required=False)
            searchbar = True
        if isinstance(field, models.DecimalField):
            filter_fields['min' + field.name] = forms.DecimalField(label='min ' + field.name, validators=field.validators, required=False)
            filter_fields['max' + field.name] = forms.DecimalField(label='max ' + field.name, validators=field.validators, required=False)
        if isinstance(field, models.IntegerField) or isinstance(field, models.PositiveIntegerField) or isinstance(field,models.PositiveSmallIntegerField):
            filter_fields['min' + field.name] = forms.IntegerField(label='min ' + field.name, validators=field.validators, required=False)
            filter_fields['max' + field.name] = forms.IntegerField(label='max ' + field.name, validators=field.validators, required=False)

    # Class name
    class_name = self.__name__ + 'FilterForm'

    # instantiate the form
    return type(form)(class_name, (form,), filter_fields)
