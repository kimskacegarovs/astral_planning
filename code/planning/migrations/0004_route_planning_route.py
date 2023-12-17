# Generated by Django 4.1 on 2023-12-17 06:36

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0003_location_shipment_location_transport_location"),
    ]

    operations = [
        migrations.CreateModel(
            name="Route",
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
                ("polyline", models.TextField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="planning",
            name="route",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="planning.route",
            ),
        ),
    ]