# -*- coding: utf-8 -*-
from modeltranslation.translator import translator, TranslationOptions
from .models import Site


class SiteTranslationOptions(TranslationOptions):
    fields = ('display_title', 'title_text')


translator.register(Site, SiteTranslationOptions)
