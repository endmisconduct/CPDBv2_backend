# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-11 08:43
from __future__ import unicode_literals
from contextlib import contextmanager
from csv import DictReader
import os
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.db import migrations

from azure.storage.blob import BlockBlobService


@contextmanager
def csv_from_azure(filename):
    block_blob_service = BlockBlobService(
        account_name=settings.DATA_PIPELINE_STORAGE_ACCOUNT_NAME,
        account_key=settings.DATA_PIPELINE_STORAGE_ACCOUNT_KEY
    )
    tmp_file = NamedTemporaryFile(suffix='.csv', delete=False)
    block_blob_service.get_blob_to_path('csv', filename, tmp_file.name)
    csvfile = open(tmp_file.name)
    reader = DictReader(csvfile)
    yield reader
    csvfile.close()
    os.remove(tmp_file.name)


def import_data(apps, schema_editor):
    Allegation = apps.get_model('data', 'Allegation')
    blank_or_null = {
        '%s_id' % field.name if field.is_relation else field.name: None if field.null else ''
        for field in Allegation._meta.get_fields()
    }

    with csv_from_azure('20180710_complaint_before_1988.csv') as reader:
        for row in reader:
            for key, val in row.iteritems():
                if val == '':
                    row[key] = blank_or_null[key]
            pk = int(row.pop('pk'))
            obj, created = Allegation.objects.update_or_create(
                id=pk,
                defaults=row
            )


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0060_merge_058_and_059'),
    ]

    operations = [
        migrations.RunPython(
                import_data,
                reverse_code=migrations.RunPython.noop,
                elidable=True),
    ]
