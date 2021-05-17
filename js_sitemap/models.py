from django.db import models
from django.utils.translation import ugettext as _

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool


class SitemapExtension(PageExtension):
    show_on_sitemap = models.BooleanField(_('Show on sitemap'), null=False, default=True)
    show_on_xml_sitemap = models.BooleanField(_('Show on xml sitemap'), null=False, default=True)
    noindex = models.BooleanField(_('noindex'), null=False, default=False)
    nofollow = models.BooleanField(_('nofollow'), null=False, default=False)
    canonical_url = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Canonical URL')
    )

extension_pool.register(SitemapExtension)
