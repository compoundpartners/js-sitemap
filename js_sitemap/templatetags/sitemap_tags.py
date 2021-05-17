# -*- coding: utf-8 -*-
from django.conf import settings
from django import template
from django.urls import reverse, resolve, NoReverseMatch
from cms.utils import get_current_site, get_language_from_request
from cms.models import Page
from menus.menu_pool import menu_pool
#from menus.utils import DefaultLanguageChanger
from cms.utils.i18n import (
    force_language,
    get_default_language_for_site,
    get_fallback_languages,
    hide_untranslated,
    is_valid_site_language,
)
from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag

register = template.Library()


class DefaultLanguageChanger(object):
    def __init__(self, request):
        self.request = request
        self._app_path = None

    @property
    def app_path(self):
        if self._app_path is None:
            if settings.USE_I18N:
                page_path = self.get_page_path(get_language_from_request(self.request))
            else:
                page_path = self.get_page_path(settings.LANGUAGE_CODE)
            if page_path:
                self._app_path = self.request.path_info[len(page_path):]
            else:
                self._app_path = self.request.path_info
        return self._app_path

    def get_public_page_path(self, lang):
        page = getattr(self.request, 'current_page', None)

        if not page:
            return ''

        page_languages = page.get_published_languages()

        if lang in page_languages and page.is_published(lang):
            return page.get_absolute_url(lang, fallback=False)
        return ''

    def get_page_path(self, lang):
        page = getattr(self.request, 'current_page', None)

        if not page:
            return ''

        page_languages = page.get_published_languages()

        if lang in page_languages and page.is_published(lang):
            return page.get_absolute_url(lang, fallback=False)

        site = get_current_site()

        if is_valid_site_language(lang, site_id=site.pk):
            _valid_language = True
            _hide_untranslated = hide_untranslated(lang, site.pk)
        else:
            _valid_language = False
            _hide_untranslated = False

        if _hide_untranslated and settings.USE_I18N:
            return '/%s/' % lang

        default_language = get_default_language_for_site(site.pk)

        if not _valid_language and default_language in page_languages:
            # The request language is not configured for the current site.
            # Fallback to the default language configured for the current site.
            return page.get_absolute_url(default_language, fallback=False)

        if _valid_language:
            fallbacks = get_fallback_languages(lang, site_id=site.pk) or []
            fallbacks = [_lang for _lang in fallbacks if _lang in page_languages]
        else:
            fallbacks = []

        if fallbacks:
            return page.get_absolute_url(fallbacks[0], fallback=False)
        return ''

    def __call__(self, lang):
        page_language = get_language_from_request(self.request)
        with force_language(page_language):
            try:
                view = resolve(self.request.path_info)
            except:
                view = None
        if hasattr(self.request, 'toolbar') and self.request.toolbar.obj and self.request.toolbar.obj.__class__ != Page:
            with force_language(lang):
                try:
                    return self.request.toolbar.obj.get_absolute_url()
                except:
                    pass
        elif view and not view.url_name in ('pages-details-by-slug', 'pages-root'):
            view_name = view.url_name
            if view.namespace:
                view_name = "%s:%s" % (view.namespace, view_name)
            url = None
            with force_language(lang):
                try:
                    url = reverse(view_name, args=view.args, kwargs=view.kwargs, current_app=view.app_name)
                except NoReverseMatch:
                    pass
            if url:
                return url
        return '%s%s' % (self.get_public_page_path(lang), self.app_path)


class PageLanguageUrl(AsTag):
    name = 'get_page_public_url'

    options = Options(
        Argument('lang'),
        'as',
        Argument('varname', required=False, resolve=False)
    )

    def get_value(self, context, lang):
        request = context.get('request', {})
        if hasattr(request, "_language_changer"):
            try:
                url = request._language_changer(lang)
            except NoReverseMatch:
                url = DefaultLanguageChanger(request)(lang)
        else:
            # use the default language changer
            url = DefaultLanguageChanger(request)(lang)
        return url


register.tag(PageLanguageUrl)
