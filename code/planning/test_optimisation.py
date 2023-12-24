import pytest
from planning.optimisation import PlanningOptimisationService
from planning.models import Shipment, Transport, Location


class TestPlanningOptimisationService:
    @pytest.fixture
    def location_new_york(self):
        return Location(latitude=40.7128, longitude=-74.0060)

    @pytest.fixture
    def location_los_angeles(self):
        return Location(latitude=34.0522, longitude=-118.2437)

    def test_calculate_distance_geopy(self, location_new_york, location_los_angeles):
        distance_km = PlanningOptimisationService().calculate_distance_geopy(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_los_angeles),
        )
        assert isinstance(distance_km, int)
        assert distance_km == 3944

    def test_calculate_distance_geopy_same_location(self, location_new_york, location_los_angeles):
        distance_km = PlanningOptimisationService().calculate_distance_geopy(
            transport=Transport(name="", location=location_new_york),
            shipment=Shipment(name="", location=location_new_york),
        )
        assert distance_km == 0
        # test pr
