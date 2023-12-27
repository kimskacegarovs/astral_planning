import pytest
from .models import Location, Shipment, Transport, Route
import json


@pytest.fixture
def transport():
    return Transport.objects.create(name="Test Transport")


@pytest.fixture
def shipment():
    return Shipment.objects.create(name="Test Shipment")


@pytest.fixture
def route():
    return Route.objects.create(polyline=json.dumps([[1.0, 2.0], [3.0, 4.0]]))


@pytest.fixture
def location():
    return Location.objects.create(latitude=50.0, longitude=30.0)
