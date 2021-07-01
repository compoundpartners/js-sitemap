# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from cms.models import Title, Page
from cms.utils import get_current_site
from cms.utils.i18n import get_public_languages
from cms.sitemaps import CMSSitemap
from .alt_sitemap import SitemapAlt


SHOW_ALTERNATIVES = getattr(
    settings,
    'SITEMAP_SHOW_ALTERNATIVES',
    False,
)

if SHOW_ALTERNATIVES:
    class CMSPageSitemap(SitemapAlt, CMSSitemap):

        def items(self):
            site = get_current_site()
            languages = get_public_languages(site_id=site.pk)
            pages = Page.objects.public().filter(
                Q(publication_date__lt=timezone.now()) | Q(publication_date__isnull=True),
                Q(publication_end_date__gte=timezone.now()) | Q(publication_end_date__isnull=True),
                login_required=False, node__site=site
                #Q(redirect__exact='') | Q(redirect__isnull=True),
                #language__in=languages,
            ).exclude(sitemapextension__show_on_xml_sitemap=False).order_by('node__path').prefetch_related('title_set')
            return pages

        def lastmod(self, page):
            modification_dates = [page.changed_date, page.publication_date]
            #plugins_for_placeholder = lambda placeholder: placeholder.get_plugins()
            #plugins = from_iterable(map(plugins_for_placeholder, page.placeholders.all()))
            #plugin_modification_dates = map(lambda plugin: plugin.changed_date, plugins)
            #modification_dates.extend(plugin_modification_dates)
            return max(modification_dates)

        def languages(self, page):
            return page.title_set.public().filter(Q(redirect__exact='') | Q(redirect__isnull=True)).values_list('language', flat=True)

else:
    class CMSPageSitemap(CMSSitemap):

        def items(self):
            site = get_current_site()
            languages = get_public_languages(site_id=site.pk)
            #all_titles = Title.objects.public().filter(
                #Q(redirect='') | Q(redirect__isnull=True),
                #language__in=languages,
                #page__login_required=False,
                #page__node__site=site,
            #).order_by('page__node__path')
            all_titles = Title.objects.public().filter(
                Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
                Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
                Q(redirect__exact='') | Q(redirect__isnull=True),
                language__in=languages, page__login_required=False, page__node__site=site
            ).exclude(page__sitemapextension__show_on_xml_sitemap=False).select_related('page').order_by('page__node__path')
            return all_titles

        def lastmod(self, title):
            modification_dates = [title.page.changed_date, title.page.publication_date]
            #plugins_for_placeholder = lambda placeholder: placeholder.get_plugins()
            #plugins = from_iterable(map(plugins_for_placeholder, title.page.placeholders.all()))
            #plugin_modification_dates = map(lambda plugin: plugin.changed_date, plugins)
            #modification_dates.extend(plugin_modification_dates)
            return max(modification_dates)



sitemaps = {
    'cmspages': CMSPageSitemap(),
}

try:
    from aldryn_newsblog.sitemaps.sitemap import NewsBlogSitemap, NewsBlogSitemapAlt
    if SHOW_ALTERNATIVES:
        sitemaps['newsblog'] = NewsBlogSitemapAlt()
    else:
        for lang, _ in settings.LANGUAGES:
            sitemaps['newsblog-%s' % lang] = NewsBlogSitemap(language=lang)
except:
    pass

try:
    from aldryn_people.sitemap import PeopleSitemap, PeopleSitemapAlt
    if SHOW_ALTERNATIVES:
        sitemaps['people'] = PeopleSitemapAlt()
    else:
        for lang, _ in settings.LANGUAGES:
            sitemaps['people-%s' % lang] = PeopleSitemap(language=lang)
except:
    pass

try:
    from js_services.sitemap import ServicesSitemap
    if SHOW_ALTERNATIVES:
        class ServicesSitemapAlt(SitemapAlt, ServicesSitemap):
            pass
        sitemaps['services'] = ServicesSitemapAlt()
    else:
        for lang, _ in settings.LANGUAGES:
            sitemaps['services-%s' % lang] = ServicesSitemap(language=lang)
except:
    pass

try:
    from js_events.sitemap import EventsSitemap
    if SHOW_ALTERNATIVES:
        class EventsSitemapAlt(SitemapAlt, EventsSitemap):
            pass
        sitemaps['events'] = EventsSitemapAlt()
    else:
        for lang, _ in settings.LANGUAGES:
            sitemaps['events-%s' % lang] = EventsSitemap(language=lang)
except:
    pass

try:
    from js_locations.sitemap import LocationsSitemap
    if SHOW_ALTERNATIVES:
        class LocationsSitemapAlt(SitemapAlt, LocationsSitemap):
            pass
        sitemaps['locations'] = LocationsSitemapAlt()
    else:
        for lang, _ in settings.LANGUAGES:
            sitemaps['locations-%s' % lang] = LocationsSitemap(language=lang)
except:
    pass
