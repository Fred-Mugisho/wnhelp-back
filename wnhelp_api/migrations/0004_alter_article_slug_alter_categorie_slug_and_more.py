# Generated by Django 5.1.6 on 2025-04-01 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wnhelp_api', '0003_remove_rapport_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(blank=True, max_length=300, unique=True),
        ),
        migrations.AlterField(
            model_name='categorie',
            name='slug',
            field=models.SlugField(max_length=300, unique=True),
        ),
        migrations.AlterField(
            model_name='rapport',
            name='slug',
            field=models.SlugField(blank=True, max_length=300, unique=True),
        ),
    ]
