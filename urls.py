# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import RedirectView, ContentView, ContentEditView, ContentDeleteView, ContentDownloadView, ContentFormView

urlpatterns = [
    # toplayer
    url(r'^$', RedirectView.as_view(), name='redirect_landing'),
    url(r'^(?P<slug>[-\w]*form[-\w]*)/$', ContentFormView.as_view(), name='form_view'), # allowing first layer form views
    url(r'^(?P<slug>[-\w]+)/$', ContentView.as_view(), name='content_view'), # always have the contentview last because its catchall
    # every other layer
    url(r'^(?P<rest_url>([-\w]+\/)*)(?P<slug>editor)/(?P<id>\d+)/$', ContentEditView.as_view(), name='editor_view'),
    url(r'^(?P<rest_url>([-\w]+\/)*)(?P<slug>delete)/(?P<id>\d+)/$', ContentDeleteView.as_view(), name='delete_view'),
    url(r'^(?P<rest_url>([-\w]+\/)*)(?P<slug>download)/(?P<id>\d+)/$', ContentDownloadView.as_view(), name='download_view'),
    url(r'^(?P<rest_url>([-\w]+\/)*)(?P<slug>[-\w]*form[-\w]*)/$', ContentFormView.as_view(), name='form_view'),
    url(r'^(?P<rest_url>([-\w]+\/)*)(?P<slug>[-\w]+)/$', ContentView.as_view(), name='content_view'),
]