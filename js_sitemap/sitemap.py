# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from cms.models import Title
from cms.utils import get_current_site
from cms.utils.i18n import get_public_languages
from cms.sitemaps import CMSSitemap


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
        ).exclude(page__sitemapextension__show_on_xml_sitemap=False).select_related('page').distinct().order_by('page__node__path')

        return all_titles


sitemaps = {
    'cmspages': CMSPageSitemap,
}

try:
    from aldryn_newsblog.sitemaps.sitemap import NewsBlogSitemap
    for lang, _ in settings.LANGUAGES:
        sitemaps['newsblog-%s' % lang] = NewsBlogSitemap(language=lang)
except:
    pass

try:
    from aldryn_people.sitemap import PeopleSitemap
    for lang, _ in settings.LANGUAGES:
        sitemaps['people-%s' % lang] = PeopleSitemap(language=lang)
except:
    pass

try:
    from js_services.sitemap import ServicesSitemap
    for lang, _ in settings.LANGUAGES:
        sitemaps['services-%s' % lang] = ServicesSitemap(language=lang)
except:
    pass

try:
    from js_events.sitemap import EventsSitemap
    for lang, _ in settings.LANGUAGES:
        sitemaps['events-%s' % lang] = EventsSitemap(language=lang)
except:
    pass

try:
    from js_locations.sitemap import LocationsSitemap
    for lang, _ in settings.LANGUAGES:
        sitemaps['locations-%s' % lang] = LocationsSitemap(language=lang)
except:
    pass
