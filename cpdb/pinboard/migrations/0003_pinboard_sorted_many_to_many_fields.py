# Generated by Django 2.1.3 on 2019-04-25 08:48

from django.db import migrations
from sortedm2m.operations import AlterSortedManyToManyField
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pinboard', '0002_add_trrs_to_pinboard'),
    ]

    operations = [
        AlterSortedManyToManyField(
            model_name='pinboard',
            name='allegations',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='data.Allegation'),
        ),
        AlterSortedManyToManyField(
            model_name='pinboard',
            name='officers',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='data.Officer'),
        ),
        AlterSortedManyToManyField(
            model_name='pinboard',
            name='trrs',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='trr.TRR'),
        ),
    ]