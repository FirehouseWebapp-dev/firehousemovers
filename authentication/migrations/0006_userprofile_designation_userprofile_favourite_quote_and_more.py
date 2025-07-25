# Generated by Django 5.1.4 on 2025-07-20 10:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0005_userprofile_profile_picture"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="designation",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="favourite_quote",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="hobbies",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="location",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="phone_number",
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="start_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
