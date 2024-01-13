import json
import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True

    def get_as_dict(self, json_vals: bool = False) -> dict:
        fields_dict = {}
        for field in self._meta.fields:
            value = getattr(self, field.name)
            if json_vals:
                value = str(value)
            fields_dict[field.name] = value
        return fields_dict

    @property
    def as_dict(self) -> dict[str, str]:
        return self.get_as_dict()

    @property
    def as_json(self) -> str:
        return json.dumps(self.get_as_dict(json_vals=True))


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
    name = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=300, null=True)
    country_code = models.CharField(max_length=2, null=True)
    postcode = models.CharField(max_length=10, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    @property
    def search_result_text(self):
        fields = [self.name, self.address, self.country_code, self.postcode]
        return ", ".join([f for f in fields if f])

    def __str__(self):
        return self.search_result_text


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

    @property
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

    def __str__(self):
        return f"Transport: {self.transport.name} - Shipment: {self.shipment.name}"
