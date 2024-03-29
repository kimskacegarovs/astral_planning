# Generated by Django 4.2.7 on 2023-11-23 06:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Planning",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Shipment",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Transport",
            fields=[
                ("id", models.UUIDField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                (
                    "plannings",
                    models.ManyToManyField(through="planning.Planning", to="planning.shipment"),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="planning",
            name="shipment",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="planning.shipment"),
        ),
        migrations.AddField(
            model_name="planning",
            name="transport",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="planning.transport"),
        ),
    ]
