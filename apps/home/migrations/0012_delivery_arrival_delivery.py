# Generated by Django 3.2.6 on 2025-01-25 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_alter_delivery_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='arrival_delivery',
            field=models.BooleanField(default=False),
        ),
    ]
