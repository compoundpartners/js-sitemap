# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from .views import basic_sitemap


urlpatterns = [
    url(r'^$', basic_sitemap, name='sitemap'),
]
