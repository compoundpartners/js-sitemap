from django.contrib import admin
from cms.extensions import PageExtensionAdmin

from .models import SitemapExtension


class SitemapExtensionAdmin(PageExtensionAdmin):
    pass

admin.site.register(SitemapExtension, SitemapExtensionAdmin)
