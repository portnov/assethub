# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-22 15:49
from __future__ import unicode_literals

import assets.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0022_component_max_thumbnail_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='big_image',
            field=models.ImageField(blank=True, null=True, upload_to=assets.models.get_big_image_path, verbose_name='larger image'),
        ),
        migrations.AddField(
            model_name='component',
            name='big_image_allowed',
            field=models.BooleanField(default=True, verbose_name='Big images are allowed'),
        ),
        migrations.AddField(
            model_name='component',
            name='max_big_image_size',
            field=models.IntegerField(default=1024, verbose_name='Maximum larger image size'),
        ),
    ]
