import numpy as np
from scipy.optimize import linear_sum_assignment
from .models import Shipment, Transport
from .geo_service import GeoService
from .types import RoutePolylineInput
from django.db.models import QuerySet
import concurrent.futures


class PlanningOptimisationService:
    def optimal_resource_allocation(self, transports: QuerySet[Transport], shipments: QuerySet[Shipment]):
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
            allocation[transports[int(i)]] = shipments[int(j)]

        return allocation

    def calculate_cost(self, transport: Transport, shipment: Shipment):
        distance = self.calculate_distance_geoservice(transport, shipment)  # Or another method
        return distance

    def calculate_distance_geoservice(self, transport: Transport, shipment: Shipment):
        transport_location = transport.location
        order_location = shipment.location
        route = GeoService().get_route(RoutePolylineInput(
            start_lat=transport_location.latitude,
            start_lon=transport_location.longitude,
            end_lat=order_location.latitude,
            end_lon=order_location.longitude
        ))
        distance_km = route.distance_km
        print(f"Distance: {distance_km} for {transport} and {shipment}")
        return distance_km

    def calculate_distance_euclidian(self, transport: Transport, shipment: Shipment):
        transport_location = np.array(transport.location.coordinates)
        order_location = np.array(shipment.location.coordinates)
        diff = transport_location - order_location
        distance = np.linalg.norm(diff)
        return distance


CALCULATE_DISTANCE_METHOD = PlanningOptimisationService.calculate_distance_geoservice
