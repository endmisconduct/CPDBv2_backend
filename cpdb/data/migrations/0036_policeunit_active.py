# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-22 08:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0035_area_police_hq'),
    ]

    operations = [
        migrations.AddField(
            model_name='policeunit',
            name='active',
            field=models.NullBooleanField(),
        ),
    ]
