import pytest
from unittest.mock import patch
from .service import PlanningService
from .models import Planning, Route, Transport, Shipment
from .types import EntityType, PlanningRequest


@pytest.mark.django_db
class TestPlanningService:
    def test_get_planning_set(self, transport, shipment):
        planning_set = PlanningService().get_planning_set()
        assert planning_set.unplanned_transports.count() == 1
        assert planning_set.unplanned_transports.first() == transport

        assert planning_set.unplanned_shipments.count() == 1
        assert planning_set.unplanned_shipments.first() == shipment

        assert planning_set.plannings.count() == 0
        assert planning_set.routes.count() == 0

        assert planning_set.total_empty_km == 0

        PlanningService().apply_optimal_planning()
        planning_set = PlanningService().get_planning_set()
        assert planning_set.plannings.count() == 1
        assert planning_set.routes.count() == 0
        assert planning_set.total_empty_km == 0

        assert planning_set.unplanned_transports.count() == 0
        assert planning_set.unplanned_shipments.count() == 0

    def test_assign_existing_routes(self, planning, route):
        assert planning.route is None

        with patch("planning.service.PlanningService.get_route_existing", return_value=route):
            PlanningService().assign_existing_routes(plannings=Planning.objects.all())
        planning.refresh_from_db()
        assert planning.route == route

    def test_get_planning_polylines(self, planning, route):
        polylines = PlanningService().get_planning_polylines(planning_set=PlanningService().get_planning_set())
        assert polylines == []

        planning.route = route
        planning.save()
        polylines = PlanningService().get_planning_polylines(planning_set=PlanningService().get_planning_set())
        assert polylines == [route.polyline_array]

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

    def test_get_route(self, transport, shipment):
        route = PlanningService().get_route(transport, shipment)
        assert isinstance(route, Route)
        assert route.location_start == transport.location
        assert route.location_end == shipment.location

    def test_apply_planning(self, transport, shipment):
        planning_request = PlanningRequest(transport_id=transport.id, shipment_id=shipment.id)
        PlanningService().apply_planning(planning_request=planning_request)
        assert Planning.objects.filter(transport=transport, shipment=shipment).exists()
        assert transport.planned_shipment == shipment

    def test_apply_optimal_planning(self, shipment, transport):
        PlanningService().apply_optimal_planning()
        plannings = Planning.objects.filter(shipment=shipment, transport=transport)
        assert plannings.count() == 1
        assert plannings.first().transport == transport
        assert plannings.first().shipment == shipment

    def test_create_entity(self, location):
        created = PlanningService().create_entity(entity_type=EntityType.TRANSPORT, name="", location=location)
        assert isinstance(created, Transport)

        created = PlanningService().create_entity(entity_type=EntityType.SHIPMENT, name="", location=location)
        assert isinstance(created, Shipment)

    def test_request_route(self, planning, route):
        assert planning.route is None

        with patch("planning.service.PlanningService.get_route", return_value=route):
            PlanningService().request_route(planning_id=planning.id)
            planning.refresh_from_db()
            assert planning.route == route
