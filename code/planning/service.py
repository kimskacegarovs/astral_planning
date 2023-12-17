from django.db.models import QuerySet, Sum
from .models import Shipment, Transport, Planning, Location, Route
from dataclasses import dataclass
from .types import RoutePolylineInput
from .geo_service import GeoService
from utils import Timer
from .optimisation import PlanningOptimisationService
from .coordinates import european_capitals


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
    def transport_factory(self, k: int):
        for i in range(k):
            location = Location().create_random_location()
            Transport(name=f"Transport {i}", location=location).save()

    def shipment_factory(self, k: int):
        for i in range(k):
            location = Location().create_random_location()
            Shipment(name=f"Shipment {i}", location=location).save()

    def main_factory(self, k: int):
        self.transport_factory(k)
        self.shipment_factory(k)

    def reset_data(self):
        Transport.objects.all().delete()
        Shipment.objects.all().delete()
        Planning.objects.all().delete()
        PlanningFactory().main_factory(k=10)

    def european_capital_factory(self):
        for i, obj in enumerate(european_capitals):
            location = Location(latitude=obj["latitude"], longitude=obj["longitude"], address=obj["address"])
            location.save()
            if i % 2 == 0:
                Transport(name=f"Transport {i}", location=location).save()
            else:
                Shipment(name=f"Shipment {i}", location=location).save()


class PlanningService:
    OPEN_ROUTE_SERVICE_USED = True  # TODO Move to settings

    def get_planning_set(self) -> PlanningSet:
        plannings = Planning.objects.all().prefetch_related("transport", "shipment")
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

    def get_planning_polylines(self, planning_set: PlanningSet):
        polylines = []
        for route in planning_set.routes:
            polylines.append(route.polyline_array)
        return polylines

    def apply_planning(self, planning_request: PlanningRequest):
        with Timer(method=self.apply_planning.__qualname__):
            transport = Transport.objects.get(id=planning_request.transport_id)
            shipment = Shipment.objects.get(id=planning_request.shipment_id)
            # route = self.get_route(transport, shipment)
            route = None
            transport.assign_shipment(shipment=shipment, route=route)

    def cancel_planning(self, planning_id: str):
        Planning.objects.get(id=planning_id).delete()

    def reset_planning(self):
        Planning.objects.all().delete()

    def get_route(self, transport: Transport, shipment: Shipment) -> Route:
        route_input = RoutePolylineInput(
            start_lat=transport.location.latitude,
            start_lon=transport.location.longitude,
            end_lat=shipment.location.latitude,
            end_lon=shipment.location.longitude,
        )
        if self.OPEN_ROUTE_SERVICE_USED:
            route = GeoService().get_route(route_input=route_input)
            return Route.objects.create(polyline=route.polyline, distance_km=route.distance_km)

    def apply_optimal_planning(self):
        planning_set = self.get_planning_set()
        optimal_planning = PlanningOptimisationService().optimal_resource_allocation(
            transports=planning_set.unplanned_transports,
            shipments=planning_set.unplanned_shipments,
        )
        for transport, shipment in optimal_planning.items():
            self.apply_planning(PlanningRequest(transport_id=transport.id, shipment_id=shipment.id))

    def request_route(self, planning_id: str):
        planning = Planning.objects.get(id=planning_id)
        route = self.get_route(planning.transport, planning.shipment)
        planning.route = route
        planning.save()
