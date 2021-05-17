# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.urls import NoReverseMatch
from django.utils import translation
from cms.utils import get_current_site
from cms.utils.i18n import get_public_languages

class SitemapAlt:

    def __get(self, name, obj, **kwargs):
        if 'default' in kwargs:
            default = kwargs.pop('default')
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj, **kwargs)
        return attr

    def location(self, obj, language=None):
        with translation.override(language or self.language):
            try:
                return obj.get_absolute_url()
            except NoReverseMatch:  # pragma: no cover
                # Note, if we did our job right in items(), this
                # shouldn't happen at all, but just in case...
                return ''

    def languages(self, obj):
        site = get_current_site()
        return get_public_languages(site_id=site.pk)
        #return [lang for lang, _ in settings.LANGUAGES]

    def _urls(self, page, protocol, domain):
        urls = []
        latest_lastmod = None
        all_items_lastmod = True  # track if all items have a lastmod
        for item in self.paginator.page(page).object_list:
            locations = []
            for lang in self.__get('languages', item):
                location = self.__get('location', item, language=lang)
                if location:
                    locations.append([lang, "%s://%s%s" % (protocol, domain, location)])
            priority = self.__get('priority', item)
            lastmod = self.__get('lastmod', item)
            if all_items_lastmod:
                all_items_lastmod = lastmod is not None
                if (all_items_lastmod and
                        (latest_lastmod is None or lastmod > latest_lastmod)):
                    latest_lastmod = lastmod
            url_info = {
                'item': item,
                'locations': locations,
                'lastmod': lastmod,
                'changefreq': self.__get('changefreq', item),
                'priority': str(priority if priority is not None else ''),
            }
            if locations:
                urls.append(url_info)
        if all_items_lastmod and latest_lastmod:
            self.latest_lastmod = latest_lastmod
        return urls
