# Generated by Django 2.1.3 on 2018-12-14 04:33

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_remove_report_page_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='slugpage',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='slugpage',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]