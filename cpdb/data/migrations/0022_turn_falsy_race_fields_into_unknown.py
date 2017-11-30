# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-30 07:30
from __future__ import unicode_literals

import data.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0021_officer_resignation_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complainant',
            name='race',
            field=models.CharField(default=b'Unknown', max_length=50, validators=[data.validators.validate_race]),
        ),
        migrations.AlterField(
            model_name='involvement',
            name='race',
            field=models.CharField(default=b'Unknown', max_length=50, validators=[data.validators.validate_race]),
        ),
        migrations.AlterField(
            model_name='officer',
            name='race',
            field=models.CharField(default=b'Unknown', max_length=50, validators=[data.validators.validate_race]),
        ),
        migrations.AlterField(
            model_name='policewitness',
            name='race',
            field=models.CharField(default=b'Unknown', max_length=50, validators=[data.validators.validate_race]),
        ),
        migrations.AlterField(
            model_name='victim',
            name='race',
            field=models.CharField(default=b'Unknown', max_length=50, validators=[data.validators.validate_race]),
        ),
    ]
