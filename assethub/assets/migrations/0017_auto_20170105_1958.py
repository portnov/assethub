# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-05 19:58
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit_autosuggest.managers
import versionfield


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0016_auto_20170105_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='notes_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='notes_ru',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='title_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='title_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='install_instructions_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='install_instructions_ru',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='notes_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='notes_ru',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='title_en',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='title_ru',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='upload_instructions_en',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='component',
            name='upload_instructions_ru',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='app_version_max',
            field=versionfield.VersionField(blank=True, null=True, verbose_name='Maximum compatible application version'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='app_version_min',
            field=versionfield.VersionField(blank=True, null=True, verbose_name='Minimum compatible application version'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assets.Application', verbose_name='application'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='component',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='assets.Component', verbose_name='component'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='data',
            field=models.FileField(upload_to='data/', verbose_name='data file'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='image',
            field=models.ImageField(upload_to='thumbnails/', verbose_name='thumbnail'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='license',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='assets.License', verbose_name='license'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='notes',
            field=models.TextField(null=True, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='original_author',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='original author'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='pub_date',
            field=models.DateTimeField(verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='tags',
            field=taggit_autosuggest.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='tags'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='url',
            field=models.URLField(blank=True, null=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='version',
            field=versionfield.VersionField(blank=True, null=True, verbose_name='asset version'),
        ),
    ]