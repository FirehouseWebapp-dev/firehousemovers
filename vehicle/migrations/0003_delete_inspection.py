# Generated by Django 5.1.4 on 2025-01-07 14:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("vehicle", "0002_availabilitydata_end_date_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Inspection",
        ),
    ]
