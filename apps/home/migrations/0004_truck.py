# Generated by Django 3.2.6 on 2024-12-29 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('home', '0003_delete_truck'),
    ]

    operations = [
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_truck', models.CharField(max_length=255)),
                ('registration_number', models.CharField(max_length=255)),
                ('model', models.CharField(max_length=255)),
                ('location', models.CharField(max_length=255)),
                ('phone', models.CharField(max_length=20)),
                ('tonnage', models.IntegerField()),
                ('insurance_date', models.DateField()),
                ('gray_card_date', models.DateField()),
            ],
            options={
                'db_table': 'truck',
            },
        ),
    ]
