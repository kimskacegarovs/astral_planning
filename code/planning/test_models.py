import json
import pytest
from .models import Location, Route, Transport, Shipment, Planning, LocationSearchResultData


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


@pytest.mark.django_db
class TestCoordinatesMixin:
    def test_coordinates(self, location):
        assert location.coordinates == (50.0, 30.0)

    def test_valid_coordinates(self, location):
        location.validate_coordinates()  # Should not raise any errors

    def test_invalid_latitude(self):
        location = Location(latitude=-100.0, longitude=30.0)
        with pytest.raises(ValueError):
            location.validate_coordinates()

    def test_invalid_longitude(self):
        location = Location(latitude=50.0, longitude=200.0)
        with pytest.raises(ValueError):
            location.validate_coordinates()

    @pytest.mark.django_db
    class TestLocationSearchResultData:
        def test_as_json(self):
            search_result = LocationSearchResultData(search_text="Test", display_name="Test", coordinates="50.0,30.0")
            search_result.save()

            expected_json = str(
                {
                    "id": str(search_result.id),
                    "search_text": "Test",
                    "display_name": "Test",
                    "coordinates": "50.0,30.0",
                }
            ).replace("'", '"')

            assert search_result.as_json == expected_json


@pytest.mark.django_db
class TestTransport:
    def test_assign_shipment(self, transport, shipment):
        planning = transport.assign_shipment(shipment)
        assert planning.transport == transport
        assert planning.shipment == shipment

    def test_unassign_shipment(self, transport, shipment):
        transport.assign_shipment(shipment)
        assert transport.plannings.count() == 1

        transport.unassign_shipment(shipment)
        assert transport.plannings.count() == 0

    def test_planned_shipment(self, transport, shipment):
        transport.assign_shipment(shipment)
        planned_shipment = transport.planned_shipment()
        assert planned_shipment == shipment


@pytest.mark.django_db
class TestRoute:
    def test_polyline_array(self):
        route = Route(polyline=json.dumps([[1.0, 2.0], [3.0, 4.0]]))
        assert route.polyline_array == [[1.0, 2.0], [3.0, 4.0]]


@pytest.mark.django_db
class TestPlanning:
    def test_planning_creation(self, transport, shipment, route):
        planning = Planning.objects.create(shipment=shipment, transport=transport, route=route)
        assert planning.shipment == shipment
        assert planning.transport == transport
        assert planning.route == route
