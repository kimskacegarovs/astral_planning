import pytest
import numpy as np
from planning.optimisation import PlanningOptimisationService
from planning.models import Shipment, Transport, Location


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

    def test_get_linear_sum_assignment(self):
        # Given cost matrix
        cost_matrix = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])

        # When get_linear_sum_assignment is called
        row_indices, col_indices = PlanningOptimisationService().get_linear_sum_assignment(cost_matrix)

        # Then optimal assignment is returned
        assert np.array_equal(row_indices, np.array([0, 1, 2]))
        assert np.array_equal(col_indices, np.array([1, 0, 2]))

    def test_optimal_resource_allocation(self):
        # Given transports and shipments
        location_0 = Location.objects.create(latitude=0, longitude=0)
        location_1 = Location.objects.create(latitude=1, longitude=1)
        location_2 = Location.objects.create(latitude=2, longitude=2)

        transport_0 = Transport.objects.create(name="transport_1", location=location_0)
        transport_1 = Transport.objects.create(name="transport_2", location=location_1)
        transport_2 = Transport.objects.create(name="transport_3", location=location_2)

        shipment_0 = Shipment.objects.create(name="shipment_1", location=location_0)
        shipment_1 = Shipment.objects.create(name="shipment_2", location=location_1)
        shipment_2 = Shipment.objects.create(name="shipment_3", location=location_2)

        # When optimal_resource_allocation is called
        allocation = PlanningOptimisationService().optimal_resource_allocation(
            transports=Transport.objects.all(),
            shipments=Shipment.objects.all(),
        )

        # Then optimal allocation is returned
        assert len(allocation) == 3
        assert allocation[transport_0] == shipment_0
        assert allocation[transport_1] == shipment_1
        assert allocation[transport_2] == shipment_2
