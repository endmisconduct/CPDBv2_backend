# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-04 07:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0023_auto_20171219_0204'),
    ]

    operations = [
        migrations.AddField(
            model_name='allegation',
            name='is_officer_complaint',
            field=models.BooleanField(default=False),
        ),
    ]
