# Generated by Django 2.2.9 on 2020-01-28 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_sitemap', '0002_auto_20190708_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemapextension',
            name='canonical_url',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Canonical URL'),
        ),
    ]
