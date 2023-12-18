import json
import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class CoordinatesMixin:
    latitude = models.FloatField()
    longitude = models.FloatField()

    @property
    def coordinates(self):
        return self.latitude, self.longitude

    def validate_coordinates(self):
        if float(self.latitude) < -90 or float(self.latitude) > 90:
            raise ValueError("Latitude must be in range [-90, 90]")
        if float(self.longitude) < -180 or float(self.longitude) > 180:
            raise ValueError("Longitude must be in range [-180, 180]")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.validate_coordinates()
        super().save()


class Location(CoordinatesMixin, BaseModel):
    # TODO Consider using GeoDjango https://docs.djangoproject.com/en/4.2/ref/contrib/gis/model-api/
    address = models.CharField(max_length=300, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Shipment(BaseModel):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)

    @property
    def plannings(self):
        return Planning.objects.filter(shipment=self)


class Transport(BaseModel):
    name = models.CharField(max_length=100)
    plannings = models.ManyToManyField(Shipment, through="Planning")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)

    def assign_shipment(self, shipment: Shipment, route: "Route" = None) -> "Planning":
        return Planning.objects.create(shipment=shipment, transport=self, route=route)

    def unassign_shipment(self, shipment: Shipment):
        Planning.objects.filter(shipment=shipment, transport=self).delete()

    def planned_shipment(self):
        # When there will be many planning, we should filter by identifier (user or session)
        return self.plannings.first()


class Route(BaseModel):
    location_start = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="route_start", null=True)
    location_end = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="route_end", null=True)
    polyline = models.TextField()
    distance_km = models.FloatField(null=True)

    @property
    def polyline_array(self):
        return json.loads(self.polyline)


class Planning(BaseModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, null=True)
