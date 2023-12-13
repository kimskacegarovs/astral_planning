from django.db.models import QuerySet
from .models import Shipment, Transport, Planning, Location
from dataclasses import dataclass


@dataclass
class PlanningSet:
    planned_transports: QuerySet[Transport]
    unplanned_transports: QuerySet[Transport]
    unplanned_shipments: QuerySet[Shipment]


@dataclass
class PlanningRequest:
    transport_id: str
    shipment_id: str


class PlanningFactory:
    def transport_factory(self, k: int):
        for i in range(k):
            location = Location().create_random_location()
            transport = Transport(name=f"Transport {i}", location=location).save()
            print(location, transport)

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


class PlanningService:
    def get_planning_set(self) -> PlanningSet:
        planned_transports = Transport.objects.filter(planning__isnull=False).prefetch_related("plannings")
        planned_shipment_ids = planned_transports.values_list("planning__shipment_id", flat=True)

        unplanned_transports = Transport.objects.filter(planning__isnull=True)
        unplanned_shipments = Shipment.objects.exclude(id__in=planned_shipment_ids)

        return PlanningSet(
            planned_transports=planned_transports,
            unplanned_transports=unplanned_transports,
            unplanned_shipments=unplanned_shipments
        )

    def apply_planning(self, planning_request: PlanningRequest):
        transport = Transport.objects.get(id=planning_request.transport_id)
        shipment = Shipment.objects.get(id=planning_request.shipment_id)
        transport.assign_shipment(shipment)

    def cancel_planning(self, planning_request: PlanningRequest):
        transport = Transport.objects.get(id=planning_request.transport_id)
        shipment = Shipment.objects.get(id=planning_request.shipment_id)
        transport.unassign_shipment(shipment)

