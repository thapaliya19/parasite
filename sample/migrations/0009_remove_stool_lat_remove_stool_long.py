# Generated by Django 4.1.3 on 2022-12-12 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0008_stool_lat_stool_long_vegetable_lat_vegetable_long_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stool",
            name="lat",
        ),
        migrations.RemoveField(
            model_name="stool",
            name="long",
        ),
    ]
