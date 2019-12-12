# Generated by Django 2.1.3 on 2019-06-17 10:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pinboard', '0004_example_pinboards'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExamplePinboard',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('pinboard', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='pinboard.Pinboard')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]