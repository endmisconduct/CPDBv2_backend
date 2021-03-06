# Generated by Django 2.2.9 on 2019-12-27 07:29

from django.db import migrations


def create_initial_toast_template(apps, schema_editor):
    Toast = apps.get_model('toast', 'Toast')
    Toast.objects.get_or_create(
        name='OFFICER',
        defaults={
            'template': '**{rank} {full_name}** {age} {race} {gender}, '
                        'with *{complaint_count} complaints*, *{sustained_count} sustained* {action_type}.',
            'tags': '{rank} {full_name} {birth_year} {gender} {race} {complaint_count} {sustained_count} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='CR',
        defaults={
            'template': '**CR #{crid}** *categorized as {category}* happened in {incident_date} {action_type}.',
            'tags': '{crid} {category} {incident_date} {action_type}'
        }
    )
    Toast.objects.get_or_create(
        name='TRR',
        defaults={
            'template': '**TRR #{id}** *categorized as {force_type}* happened in {incident_date} {action_type}.',
            'tags': '{id} {force_type} {incident_date} {action_type}'
        }
    )


def remove_initial_toast_template(apps, schema_editor):
    Toast = apps.get_model('toast', 'Toast')
    templates = Toast.objects.filter(name__in=['OFFICER', 'CR', 'TRR'])
    templates.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('toast', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_initial_toast_template,
            reverse_code=remove_initial_toast_template,
        )
    ]
