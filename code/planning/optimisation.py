import concurrent.futures

import numpy as np
from django.db.models import QuerySet
from geopy.distance import geodesic
from scipy.optimize import linear_sum_assignment

from .geo_service import GeoService
from .models import Route, Shipment, Transport
from .types import RoutePolylineInput


class PlanningOptimisationService:
    MAX_EMPTY_KM = 3_000

    def optimal_resource_allocation(
        self, transports: QuerySet[Transport], shipments: QuerySet[Shipment], max_empty_km: int = None
    ):
        max_empty_km = max_empty_km or self.MAX_EMPTY_KM
        num_transports = len(transports)
        num_orders = len(shipments)
        cost_matrix = np.zeros((num_transports, num_orders))

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

        # Use the Hungarian algorithm to find the optimal assignment.
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Create a dictionary to store the optimal allocation.
        allocation = {}
        for i, j in zip(row_indices, col_indices):
            if cost_matrix[i][j] > max_empty_km:
                continue
            allocation[transports[int(i)]] = shipments[int(j)]

        return allocation

    def calculate_cost(self, transport: Transport, shipment: Shipment):
        distance_km = self.get_distance(transport, shipment)
        return distance_km

    def get_distance(self, transport: Transport, shipment: Shipment):
        existing_routes = Route.objects.filter(location_start=transport.location, location_end=shipment.location)
        if existing_routes:
            return existing_routes.first().distance_km

        distance_km = CALCULATE_DISTANCE_METHOD(self, transport, shipment)
        return distance_km

    def calculate_distance_geoservice(self, transport: Transport, shipment: Shipment):
        transport_location = transport.location
        order_location = shipment.location
        route = GeoService().get_route(
            RoutePolylineInput(
                start_lat=transport_location.latitude,
                start_lon=transport_location.longitude,
                end_lat=order_location.latitude,
                end_lon=order_location.longitude,
            )
        )
        distance_km = round(route.distance_km)
        return distance_km

    def calculate_distance_geopy(self, transport: Transport, shipment: Shipment):
        transport_location = transport.location
        order_location = shipment.location
        distance = geodesic(transport_location.coordinates, order_location.coordinates).km
        return round(distance)


# Change this to switch between the methods
CALCULATE_DISTANCE_METHOD = PlanningOptimisationService.calculate_distance_geopy
