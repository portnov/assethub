# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-07 06:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flatmenu', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='title_en',
            field=models.CharField(max_length=255, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='menuitem',
            name='title_ru',
            field=models.CharField(max_length=255, null=True, verbose_name='Title'),
        ),
    ]