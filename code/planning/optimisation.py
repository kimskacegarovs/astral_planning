import concurrent.futures

import numpy as np
from django.db.models import QuerySet
from geopy.distance import geodesic
from scipy.optimize import linear_sum_assignment

from .models import Route, Shipment, Transport
from utils import timer


class PlanningOptimisationService:
    MAX_EMPTY_KM = 3_000

    @timer()
    def optimal_resource_allocation(
        self, transports: QuerySet[Transport], shipments: QuerySet[Shipment], max_empty_km: int = None
    ):
        max_empty_km = max_empty_km or self.MAX_EMPTY_KM
        cost_matrix = np.zeros((len(transports), len(shipments)))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.calculate_cost, transport, shipment): (i, j)
                for i, transport in enumerate(transports)
                for j, shipment in enumerate(shipments)
            }

            for future in concurrent.futures.as_completed(futures):
                i, j = futures[future]
                cost = future.result()
                cost_matrix[i][j] = cost

        row_indices, col_indices = self.get_linear_sum_assignment(cost_matrix)

        # Create a dictionary to store the optimal allocation.
        allocation = {}
        for i, j in zip(row_indices, col_indices):
            if cost_matrix[i][j] > max_empty_km:
                continue
            allocation[transports[int(i)]] = shipments[int(j)]

        return allocation

    def get_linear_sum_assignment(self, cost_matrix):
        # Use the Hungarian algorithm to find the optimal assignment.
        row_indices, col_indices = linear_sum_assignment(cost_matrix)
        return row_indices, col_indices

    def calculate_cost(self, transport: Transport, shipment: Shipment):
        distance_km = self.get_distance(transport, shipment)
        return distance_km

    def get_distance(self, transport: Transport, shipment: Shipment):
        existing_routes = Route.objects.filter(location_start=transport.location, location_end=shipment.location)
        if existing_routes:
            return existing_routes.first().distance_km

        distance_km = self.calculate_distance_geopy(transport=transport, shipment=shipment)
        return distance_km

    def calculate_distance_geopy(self, transport: Transport, shipment: Shipment):
        transport_location = transport.location
        order_location = shipment.location
        distance = geodesic(transport_location.coordinates, order_location.coordinates).km
        return round(distance)
