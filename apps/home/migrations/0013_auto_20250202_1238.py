# Generated by Django 3.2.6 on 2025-02-02 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_delivery_arrival_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='jour_ferie',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='delivery',
            name='weekend',
            field=models.BooleanField(default=False),
        ),
    ]
