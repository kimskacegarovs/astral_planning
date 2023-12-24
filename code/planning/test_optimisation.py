import pytest
from planning.optimisation import PlanningOptimisationService
from planning.models import Shipment, Transport, Location, Route


@pytest.mark.django_db
class TestPlanningOptimisationService:
    @pytest.fixture
    def geopy_ny_to_la_km(self):
        return 3944

    @pytest.fixture
    def location_new_york(self):
        return Location(latitude=40.7128, longitude=-74.0060)

    @pytest.fixture
    def location_los_angeles(self):
        return Location(latitude=34.0522, longitude=-118.2437)

    def test_calculate_distance_geopy(self, location_new_york, location_los_angeles, geopy_ny_to_la_km):
        distance_km = PlanningOptimisationService().calculate_distance_geopy(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_los_angeles),
        )
        assert isinstance(distance_km, int)
        assert distance_km == geopy_ny_to_la_km

    def test_calculate_distance_geopy_same_location(self, location_new_york, location_los_angeles):
        distance_km = PlanningOptimisationService().calculate_distance_geopy(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_new_york),
        )
        assert distance_km == 0

    def test_get_distance_no_existing_route(self, location_new_york, location_los_angeles, geopy_ny_to_la_km):
        # Given no Route instances stored for given locations
        Route.objects.all().delete()

        # When get_distance is called
        distance_km = PlanningOptimisationService().get_distance(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_los_angeles),
        )

        # Then geopy distance is returned
        assert distance_km == geopy_ny_to_la_km

    def test_get_distance_existing_route(self, location_new_york, location_los_angeles):
        # Given Route instance stored for given locations
        route_distance_km = 123
        location_new_york.save()
        location_los_angeles.save()
        Route.objects.create(
            location_start=location_new_york,
            location_end=location_los_angeles,
            polyline="",
            distance_km=route_distance_km,
        )

        # When get_distance is called
        distance_km = PlanningOptimisationService().get_distance(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_los_angeles),
        )

        # Then distance from Route is returned
        assert distance_km == route_distance_km

