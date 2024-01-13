import numpy as np
from django.db.models import QuerySet, Q
from geopy.distance import geodesic
from scipy.optimize import linear_sum_assignment

from .models import Route, Shipment, Transport
from utils import timer
from typing import Dict
from uuid import UUID

import rust_cost_matrix  # pyO3 rust module

ExistingRouteDistances = Dict[tuple[UUID, UUID], int]


class PlanningOptimisationService:
    DEFAULT_MAX_EMPTY_KM = 3_000

    @timer()
    def optimal_resource_allocation(
        self, transports: QuerySet[Transport], shipments: QuerySet[Shipment], max_empty_km: int = None
    ) -> dict[Transport, Shipment]:
        max_empty_km = max_empty_km or self.DEFAULT_MAX_EMPTY_KM
        cost_matrix = self.get_cost_matrix(transports=transports, shipments=shipments, max_empty_km=max_empty_km)
        row_indices, col_indices = self.get_linear_sum_assignment(cost_matrix)

        allocation = {}
        for i, j in zip(row_indices, col_indices):
            if cost_matrix[i][j] > max_empty_km:
                continue
            allocation[transports[int(i)]] = shipments[int(j)]

        return allocation

    def get_linear_sum_assignment(self, cost_matrix) -> tuple[np.ndarray, np.ndarray]:
        # Use the Hungarian algorithm to find the optimal assignment.
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        return row_indices, col_indices

    @timer()
    def get_cost_matrix(
        self, transports: QuerySet[Transport], shipments: QuerySet[Shipment], max_empty_km: int
    ) -> np.ndarray:
        existing_route_distances = self.get_existing_routes(transports, shipments)
        transport_locations = transports.values_list("location__id", flat=True)
        shipment_locations = shipments.values_list("location__id", flat=True)

        cost_matrix = np.zeros((len(transports), len(shipments)))

        for i, transport_location in enumerate(transport_locations):
            for j, shipment_location in enumerate(shipment_locations):
                key = (transport_location, shipment_location)
                if existing_route_distance := existing_route_distances.get(key):
                    distance_km = existing_route_distance
                else:
                    distance_km = self.calculate_distance_rust(transports[i], shipments[j])

                cost_matrix[i, j] = distance_km if distance_km < max_empty_km else 1_000_000

        return cost_matrix

    @timer()
    def get_existing_routes(
        self, transports: QuerySet[Transport], shipments: QuerySet[Shipment]
    ) -> ExistingRouteDistances:
        existing_routes = Route.objects.filter(
            Q(location_start__in=transports.values("location")) & Q(location_end__in=shipments.values("location"))
        ).values("location_start", "location_end", "distance_km")

        routes_dict: ExistingRouteDistances = {}
        for route in existing_routes:
            key = (route["location_start"], route["location_end"])
            routes_dict[key] = route["distance_km"]

        return routes_dict

    def calculate_distance_rust(self, transport: Transport, shipment: Shipment) -> int:
        distance_km = rust_cost_matrix.calculate_distance(
            transport.location.latitude,
            transport.location.longitude,
            shipment.location.latitude,
            shipment.location.longitude,
        )
        return round(distance_km)

    def calculate_distance_geopy(self, transport: Transport, shipment: Shipment) -> int:
        transport_location = transport.location
        order_location = shipment.location
        distance_km = geodesic(transport_location.coordinates, order_location.coordinates).km
        return round(distance_km)
