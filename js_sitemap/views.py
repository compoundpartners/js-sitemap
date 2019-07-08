# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.response import TemplateResponse
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import get_language_from_request

from cms.models import Title


def get_language(request):
    lang = getattr(request, 'LANGUAGE_CODE', None)
    if lang is None:
        lang = get_language_from_request(request, check_path=True)
    return lang


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
        language=language
    ).exclude(page__sitemapextension__show_on_sitemap=False).select_related('page').distinct()

    titles = {}
    by_parent = {}
    for title in cms_titles:
        titles[title.page.pk] = title
        if title.page.parent_id in by_parent:
            by_parent[title.page.parent_id].append(title.page.pk)
        else:
            by_parent[title.page.parent_id] = []

    urls = []
    for title in titles.values():
        if not title.page.parent:
            item = {'title': title.title, 'url': title.page.get_absolute_url(), 'children':[]}
            if title.page.pk in by_parent and len(by_parent[title.page.pk]) > 0:
                for key in by_parent[title.page.pk]:
                    item2 = {'title': titles[key].title, 'url': titles[key].page.get_absolute_url(), 'children':[]}
                    if key in by_parent and len(by_parent[key]) > 0:
                        for key2 in by_parent[key]:
                            item2['children'].append({'title': titles[key2].title, 'url': titles[key2].page.get_absolute_url(), 'children':None})
                    item['children'].append(item2)
            urls.append(item)

    response = TemplateResponse(request, 'js_sitemap/sitemap.html', {'urlset': urls})

    return response
