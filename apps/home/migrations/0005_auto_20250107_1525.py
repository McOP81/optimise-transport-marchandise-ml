# Generated by Django 3.2.6 on 2025-01-07 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_truck'),
    ]

    operations = [
        migrations.AlterField(
            model_name='truck',
            name='name_truck',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='truck',
            name='registration_number',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
