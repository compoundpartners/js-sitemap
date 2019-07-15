# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.response import TemplateResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import get_language_from_request
from django.conf import settings
from django.views.decorators.cache import cache_page

from cms.models import Title
from cms.apphook_pool import apphook_pool

APPLICATIONS = {}

SITEMAP_CACHE_TIMEOUT = getattr(
    settings,
    'SITEMAP_CACHE_TIMEOUT',
    60*60*24,
)

try:
    from aldryn_newsblog.sitemaps.sitemap import NewsBlogSitemap
    from aldryn_newsblog.cms_apps import NewsBlogApp
    APPLICATIONS[NewsBlogApp] = NewsBlogSitemap
except:
    pass

try:
    from aldryn_people.sitemap import PeopleSitemap
    from aldryn_people.cms_apps import PeopleApp
    APPLICATIONS[PeopleApp] = PeopleSitemap
except:
    pass

try:
    from js_services.sitemap import ServicesSitemap
    from js_services.cms_apps import ServicesApp
    APPLICATIONS[ServicesApp] = ServicesSitemap
except:
    pass

try:
    from js_events.sitemap import EventsSitemap
    from js_events.cms_apps import EventsApp
    APPLICATIONS[EventsApp] = EventsSitemap
except:
    pass

try:
    from js_locations.sitemap import LocationsSitemap
    from js_locations.cms_apps import JSLocationsApp
    APPLICATIONS[JSLocationsApp] = LocationsSitemap
except:
    pass


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang


@cache_page(SITEMAP_CACHE_TIMEOUT)
def basic_sitemap(request, **kwargs):
    """View for a human friendly sitemap."""
    language = get_language(request)

    #cms_titles = Title.objects.public().filter(
            #Q(redirect='') | Q(redirect__isnull=True),
            #page__login_required=False, language=request.LANGUAGE_CODE,
            #page__parent=None)\
            #.exclude(sitemapextension__show_on_sitemap=False)\
            #.order_by('title')

    cms_titles =  Title.objects.public().filter(
        Q(page__publication_date__lt=timezone.now()) | Q(page__publication_date__isnull=True),
        Q(page__publication_end_date__gte=timezone.now()) | Q(page__publication_end_date__isnull=True),
        Q(redirect__exact='') | Q(redirect__isnull=True),
        language=language, page__login_required=False
    ).exclude(page__sitemapextension__show_on_sitemap=False).select_related('page').distinct()

    titles = {}
    by_parent = {}
    children = {}
    for title in cms_titles:
        titles[title.page.pk] = title
        if title.page.parent_page:
            parent_id = title.page.parent_page.pk
            if parent_id in by_parent:
                by_parent[parent_id].append(title.page.pk)
            else:
                by_parent[parent_id] = [title.page.pk]
        if title.page.application_urls:
            app = apphook_pool.get_apphook(title.page.application_urls)
            if app and app.__class__ in APPLICATIONS:
                kwargs = {'type': 'html', 'language':language}
                if app.app_config:
                    kwargs['namespace'] = title.page.application_namespace
                sitemap = APPLICATIONS[app.__class__](**kwargs)
                items = []
                for item in sitemap.items():
                    url = sitemap.location(item)
                    if url:
                        items.append({'title': str(item), 'url': url})
                if items:
                    children[title.page.pk] = items

    def get_item(title):
        nonlocal titles, by_parent, children
        item = {'title': title.title, 'url': title.page.get_absolute_url(), 'children':[]}
        if title.page.pk in children:
            item['children'] = children[title.page.pk]
            return item
        if title.page.pk in by_parent and len(by_parent[title.page.pk]) > 0:
            for key in by_parent[title.page.pk]:
                item['children'].append(get_item(titles[key]))
            del by_parent[title.page.pk]
        return item
        if title.page.parent_page and not by_parent:
            return

    urls = []
    for title in titles.values():
        if not title.page.parent_page:
            urls.append(get_item(title))

    response = TemplateResponse(request, 'js_sitemap/sitemap.html', {'urlset': urls})

    return response

