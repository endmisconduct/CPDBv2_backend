# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-30 08:46
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
    InvestigatorAllegation = apps.get_model('data', 'InvestigatorAllegation')
    blank_or_null = {
        '%s_id' % field.name if field.is_relation else field.name: None if field.null else ''
        for field in InvestigatorAllegation._meta.get_fields()
    }
    pks = []

    with csv_from_azure('20180530_investigatorallegation.csv') as reader:
        for row in reader:
            for key, val in row.iteritems():
                if val == '':
                    row[key] = blank_or_null[key]
            pk = int(row.pop('pk'))
            pks.append(pk)
            obj, created = InvestigatorAllegation.objects.update_or_create(
                id=pk,
                defaults=row
            )

    InvestigatorAllegation.objects.exclude(pk__in=pks).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0049_import_investigator_data'),
    ]

    operations = [
        migrations.RunPython(
                import_data,
                reverse_code=migrations.RunPython.noop,
                elidable=True),
    ]
