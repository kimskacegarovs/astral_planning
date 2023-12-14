from django.db import models
import random
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Location(BaseModel):
    # TODO Consider using GeoDjango https://docs.djangoproject.com/en/4.2/ref/contrib/gis/model-api/
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

    @classmethod
    def create_random_location(cls):
        uzbekistan_latitude_range = (37, 45)  # Latitude range of Uzbekistan
        uzbekistan_longitude_range = (56, 73)  # Longitude range of Uzbekistan

        instance = cls(
            latitude=random.uniform(*uzbekistan_latitude_range),
            longitude=random.uniform(*uzbekistan_longitude_range)
        )
        instance.save()
        return instance


class Shipment(BaseModel):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)

    @property
    def plannings(self):
        return Planning.objects.filter(shipment=self)


class Transport(BaseModel):
    name = models.CharField(max_length=100)
    plannings = models.ManyToManyField(Shipment, through='Planning')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)

    def assign_shipment(self, shipment: Shipment):
        Planning.objects.create(shipment=shipment, transport=self)

    def unassign_shipment(self, shipment: Shipment):
        Planning.objects.filter(shipment=shipment, transport=self).delete()

    def planned_shipment(self):
        # When there will be many planning, we should filter by identifier (user or session)
        return self.plannings.first()


class Planning(BaseModel):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)