# Generated by Django 4.1 on 2023-12-17 14:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("planning", "0005_route_distance_km"),
    ]

    operations = [
        migrations.AddField(
            model_name="location",
            name="address",
            field=models.CharField(max_length=300, null=True),
        ),
    ]
