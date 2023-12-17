# Generated by Django 4.2.7 on 2023-11-23 08:53

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0002_alter_planning_id_alter_shipment_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Location",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("latitude", models.FloatField()),
                ("longitude", models.FloatField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="shipment",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="planning.location",
            ),
        ),
        migrations.AddField(
            model_name="transport",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="planning.location",
            ),
        ),
    ]