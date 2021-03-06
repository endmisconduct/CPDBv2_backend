# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-04 03:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_cloud', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='documentcrawler',
            name='num_new_documents',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='documentcrawler',
            name='num_updated_documents',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='documentcrawler',
            name='num_documents',
            field=models.IntegerField(default=0),
        ),
    ]
