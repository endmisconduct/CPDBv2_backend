# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-02-09 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0006_officer_rank_freeform'),
        ('cms', '0008_faqpage_starred'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportpage',
            name='officers',
            field=models.ManyToManyField(to='data.Officer'),
        ),
    ]
