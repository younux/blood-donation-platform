# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-26 17:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='country',
            field=models.CharField(default='Maroc', max_length=64, verbose_name='Country'),
            preserve_default=False,
        ),
    ]
