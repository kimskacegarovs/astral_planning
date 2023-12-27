import pytest
from .service import PlanningService
from .models import Planning, Route


@pytest.mark.django_db
class TestPlanningService:
    def test_cancel_planning(self, planning):
        PlanningService().cancel_planning(planning_id=planning.id)
        assert Planning.objects.filter(id=planning.id).exists() is False

    def test_reset_planning(self, planning):
        PlanningService().reset_planning()
        assert Planning.objects.all().exists() is False

    def test_get_route_existing_none(self, transport, shipment):
        route = PlanningService().get_route_existing(transport, shipment)
        assert route is None

    def test_get_route_existing_exits(self, transport, shipment):
        route = Route.objects.create(location_start=transport.location, location_end=shipment.location)
        assert PlanningService().get_route_existing(transport, shipment) == route

    def test_apply_optimal_planning(self, shipment, transport):
        PlanningService().apply_optimal_planning()
        plannings = Planning.objects.filter(shipment=shipment, transport=transport)
        assert plannings.count() == 1
        assert plannings.first().transport == transport
        assert plannings.first().shipment == shipment
