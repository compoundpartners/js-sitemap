# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-08 13:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_sitemap', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemapextension',
            name='nofollow',
            field=models.BooleanField(default=False, verbose_name='nofollow'),
        ),
        migrations.AddField(
            model_name='sitemapextension',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='noindex'),
        ),
        migrations.AddField(
            model_name='sitemapextension',
            name='show_on_xml_sitemap',
            field=models.BooleanField(default=True, verbose_name='Show on xml sitemap'),
        ),
    ]