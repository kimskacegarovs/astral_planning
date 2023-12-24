from dataclasses import dataclass

from django.db.models import QuerySet, Sum
from utils import timer

from .coordinates import european_capitals
from .geo_service import GeoService
from .models import Location, Planning, Route, Shipment, Transport
from .optimisation import PlanningOptimisationService
from .types import RoutePolylineInput


@dataclass
class PlanningSet:
    plannings: QuerySet[Planning]
    routes: QuerySet[Route]
    unplanned_transports: QuerySet[Transport]
    unplanned_shipments: QuerySet[Shipment]
    total_empty_km: float


@dataclass
class PlanningRequest:
    transport_id: str
    shipment_id: str


class PlanningFactory:
    def reset_data(self):
        Transport.objects.all().delete()
        Shipment.objects.all().delete()
        Planning.objects.all().delete()

    def european_capital_factory(self):
        for i, obj in enumerate(european_capitals):
            location = Location(latitude=obj["latitude"], longitude=obj["longitude"], address=obj["address"])
            location.save()
            if i % 2 == 0:
                Transport(name=f"Transport {i}", location=location).save()
            else:
                Shipment(name=f"Shipment {i}", location=location).save()


class PlanningService:
    def get_planning_set(self) -> PlanningSet:
        plannings = Planning.objects.all().prefetch_related("transport", "shipment")
        self.assign_routes(plannings=plannings.filter(route__isnull=True))

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

    def assign_routes(self, plannings: QuerySet[Planning]):
        for planning in plannings:
            if existing_route := self.get_route_existing(planning.transport, planning.shipment):
                planning.route = existing_route
                planning.save()

    def get_planning_polylines(self, planning_set: PlanningSet):
        polylines = []
        for route in planning_set.routes:
            polylines.append(route.polyline_array)
        return polylines

    @timer()
    def apply_planning(self, planning_request: PlanningRequest):
        transport = Transport.objects.get(id=planning_request.transport_id)
        shipment = Shipment.objects.get(id=planning_request.shipment_id)
        route = self.get_route_existing(transport, shipment)
        transport.assign_shipment(shipment=shipment, route=route)

    def cancel_planning(self, planning_id: str):
        Planning.objects.get(id=planning_id).delete()

    def reset_planning(self):
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
        for transport, shipment in optimal_planning.items():
            self.apply_planning(PlanningRequest(transport_id=transport.id, shipment_id=shipment.id))

    def request_route(self, planning_id: str):
        planning = Planning.objects.filter(id=planning_id).first()
        if not planning:
            return None
        route = self.get_route(planning.transport, planning.shipment)
        planning.route = route
        planning.save()
