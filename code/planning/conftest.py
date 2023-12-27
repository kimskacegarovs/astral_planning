import pytest
from .models import Location, Shipment, Transport, Route, Planning
import json


@pytest.fixture
def location():
    return Location.objects.create(latitude=50.0, longitude=30.0)


@pytest.fixture
def transport(location):
    return Transport.objects.create(name="Test Transport", location=location)


@pytest.fixture
def shipment(location):
    return Shipment.objects.create(name="Test Shipment", location=location)


@pytest.fixture
def route():
    return Route.objects.create(polyline=json.dumps([[1.0, 2.0], [3.0, 4.0]]))


@pytest.fixture
def planning(transport, shipment):
    return Planning.objects.create(transport=transport, shipment=shipment)
