# Generated by Django 4.1.3 on 2023-03-27 05:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0016_remove_slideimage_annotated_and_more"),
        ("annotation", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Annotation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label_file", models.FileField(upload_to="annotation/labels")),
                ("annotated", models.BooleanField(default=False)),
                (
                    "annotator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="annotation.annotator",
                    ),
                ),
                (
                    "image",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="annotation_image",
                        to="sample.slideimage",
                    ),
                ),
            ],
            options={
                "unique_together": {("image", "annotator")},
            },
        ),
    ]
