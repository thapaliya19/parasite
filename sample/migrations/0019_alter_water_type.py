# Generated by Django 4.1.3 on 2024-07-01 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0018_slideimage_comment_slideimage_reviewed"),
    ]

    operations = [
        migrations.AlterField(
            model_name="water",
            name="type",
            field=models.CharField(
                choices=[
                    ("RI", "River"),
                    ("BO", "Bottled"),
                    ("JA", "Jar"),
                    ("LA", "Lake"),
                    ("WL", "Wetland"),
                    ("WW", "Well Water"),
                    ("DB", "Deep Boring"),
                    ("PW", "Pond Water"),
                    ("ST", "Stream"),
                    ("SW", "Spring Water"),
                    ("MT", "Tap (Municipal Tap)"),
                    ("TA", "Tap (Tanker)"),
                    ("TU", "Tap (Tubewell)"),
                    ("DH", "Tap (Dhungedhara)"),
                    ("BR", "Tap (Boring)"),
                    ("FL", "Tap (Filter)"),
                    ("WT", "Tap (Water Tank)"),
                    ("TP", "Tap Water"),
                ],
                max_length=2,
            ),
        ),
    ]