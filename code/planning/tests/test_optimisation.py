import pytest
from unittest.mock import Mock
from ..models import Shipment, Transport


class TestPlanningOptimisationService:
    @pytest.fixture()
    def location_new_york(self):
        ...

    def test_calculate_distance_geopy(self, planning_service):
        # Given
        transport = Transport(location=Mock(coordinates=(40.7128, -74.0060)))  # New York coordinates
        shipment = Shipment(location=Mock(coordinates=(34.0522, -118.2437)))  # Los Angeles coordinates

        # When
        distance = planning_service.calculate_distance_geopy(transport, shipment)

        # Then
        assert isinstance(distance, int)  # Ensure distance is an integer after rounding
        assert distance > 0  # Ensure distance is positive

    def test_calculate_distance_geopy_same_location(self, planning_service):
        # Given
        coordinates = (51.5074, -0.1278)  # London coordinates for both transport and shipment
        transport = Transport(location=Mock(coordinates=coordinates))
        shipment = Shipment(location=Mock(coordinates=coordinates))

        # When
        distance = planning_service.calculate_distance_geopy(transport, shipment)

        # Then
        assert distance == 0  # Ensure distance is 0 when locations are the same
