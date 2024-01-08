from django.db.models import QuerySet, Sum
from django.db import transaction
from utils import timer
from typing import Optional

from .geo_service import GeoService
from .models import Planning, Route, Shipment, Transport, Location
from .optimisation import PlanningOptimisationService
from .types import RoutePolylineInput, EntityType, PlanningSet, PlanningRequest


class PlanningService:
    def get_planning_set(self) -> PlanningSet:
        plannings = Planning.objects.all().prefetch_related("transport", "shipment")
        self.assign_existing_routes(plannings=plannings.filter(route__isnull=True))

        routes = Route.objects.filter(id__in=plannings.values_list("route"))
        planned_transports = Transport.objects.filter(id__in=plannings.values_list("transport"))
        planned_shipment_ids = planned_transports.values_list("planning__shipment_id", flat=True)

        unplanned_transports = Transport.objects.filter(planning__isnull=True)
        unplanned_shipments = Shipment.objects.exclude(id__in=planned_shipment_ids)

        total_empty_km = round(routes.aggregate(total_empty_km=Sum("distance_km"))["total_empty_km"]) if routes else 0

        return PlanningSet(
            plannings=plannings,
            unplanned_transports=unplanned_transports,
            unplanned_shipments=unplanned_shipments,
            routes=routes,
            total_empty_km=total_empty_km,
        )

    @timer()
    def get_center_coordinate(self, planning_set: PlanningSet) -> Optional[list[float]]:
        planned_transport_lats = planning_set.plannings.values_list("transport__location__latitude", flat=True)
        planned_transport_lons = planning_set.plannings.values_list("transport__location__longitude", flat=True)

        planned_shipment_lats = planning_set.plannings.values_list("shipment__location__latitude", flat=True)
        planned_shipment_lons = planning_set.plannings.values_list("shipment__location__longitude", flat=True)

        unplanned_transport_lats = planning_set.unplanned_transports.values_list("location__latitude", flat=True)
        unplanned_transport_lons = planning_set.unplanned_transports.values_list("location__longitude", flat=True)

        unplanned_shipment_lats = planning_set.unplanned_shipments.values_list("location__latitude", flat=True)
        unplanned_shipment_lons = planning_set.unplanned_shipments.values_list("location__longitude", flat=True)

        def sum_qs(qs1, qs2, qs3, qs4) -> int:
            return sum(list(qs1) + list(qs2) + list(qs3) + list(qs4))

        num_coords = (
            len(planned_transport_lats)
            + len(planned_shipment_lats)
            + len(unplanned_transport_lats)
            + len(unplanned_shipment_lats)
        )
        if num_coords > 0:
            avg_lat = (
                sum_qs(
                    planned_transport_lats, planned_shipment_lats, unplanned_transport_lats, unplanned_shipment_lats
                )
                / num_coords
            )

            avg_lon = (
                sum_qs(
                    planned_transport_lons, planned_shipment_lons, unplanned_transport_lons, unplanned_shipment_lons
                )
                / num_coords
            )

            return [avg_lat, avg_lon]
        return [0, 0]

    def assign_existing_routes(self, plannings: QuerySet[Planning]) -> None:
        for planning in plannings:
            if existing_route := self.get_route_existing(planning.transport, planning.shipment):
                planning.route = existing_route
                planning.save()

    def get_planning_polylines(self, planning_set: PlanningSet) -> list[list[list[float]]]:
        return [route.polyline_array for route in planning_set.routes]

    @timer()
    def apply_planning(self, planning_request: PlanningRequest):
        transport = Transport.objects.get(id=planning_request.transport_id)
        shipment = Shipment.objects.get(id=planning_request.shipment_id)
        route = self.get_route(transport, shipment)
        transport.assign_shipment(shipment=shipment, route=route)

    def cancel_planning(self, planning_id: str):
        Planning.objects.get(id=planning_id).delete()

    def reset_planning(self):
        # TODO This should be filtered by identifier (user or session)
        Planning.objects.all().delete()

    def get_route_existing(self, transport: Transport, shipment: Shipment) -> Route | None:
        existing_routes = Route.objects.filter(location_start=transport.location, location_end=shipment.location)
        if existing_routes:
            return existing_routes.first()
        return None

    def get_route(self, transport: Transport, shipment: Shipment) -> Route:
        if existing_route := self.get_route_existing(transport, shipment):
            return existing_route

        route_input = RoutePolylineInput(
            start_lat=transport.location.latitude,
            start_lon=transport.location.longitude,
            end_lat=shipment.location.latitude,
            end_lon=shipment.location.longitude,
        )
        route = GeoService().get_route(route_input=route_input)
        return Route.objects.create(
            location_start=transport.location,
            location_end=shipment.location,
            polyline=route.polyline,
            distance_km=route.distance_km,
        )

    @timer()
    def apply_optimal_planning(self, max_empty_km: int = None):
        max_empty_km = int(max_empty_km) if max_empty_km else None
        planning_set = self.get_planning_set()
        optimal_planning = PlanningOptimisationService().optimal_resource_allocation(
            max_empty_km=max_empty_km,
            transports=planning_set.unplanned_transports,
            shipments=planning_set.unplanned_shipments,
        )
        plannings = []
        for transport, shipment in optimal_planning.items():
            plannings.append(Planning(transport=transport, shipment=shipment))
        with transaction.atomic():
            Planning.objects.bulk_create(plannings)

    def request_route(self, planning: Optional[Planning] = None, planning_id: Optional[str] = None) -> None:
        if not any([planning, planning_id]):
            raise ValueError("Either planning or planning_id must be provided")
        planning = Planning.objects.get(id=planning_id) if not planning else planning
        planning.route = self.get_route(planning.transport, planning.shipment)
        planning.save()

    def create_entity(self, entity_type: EntityType, name: str, location: Location) -> Shipment | Transport:
        match entity_type:
            case EntityType.SHIPMENT:
                return Shipment.objects.create(location=location, name=name)
            case EntityType.TRANSPORT:
                return Transport.objects.create(location=location, name=name)

    @timer()
    def create_entities(self):
        Shipment.objects.all().delete()
        Transport.objects.all().delete()

        count = 120
        lv_locations = Location.objects.filter(country_code="LV")

        for i in range(count):
            entity_type = EntityType.SHIPMENT if i % 2 == 0 else EntityType.TRANSPORT
            self.create_entity(
                entity_type=entity_type,
                name=f"{entity_type.name} {i}",
                location=lv_locations[i],
            )
