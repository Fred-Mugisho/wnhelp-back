# Generated by Django 5.1.6 on 2025-07-11 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wnhelp_api', '0009_alter_joboffer_options_joboffer_counter_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='joboffer',
            name='reference',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]
