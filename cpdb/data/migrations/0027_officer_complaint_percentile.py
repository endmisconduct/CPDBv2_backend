# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-29 06:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0026_add_investigatorallegation'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='complaint_percentile',
            field=models.DecimalField(decimal_places=3, max_digits=6, null=True),
        ),
    ]
