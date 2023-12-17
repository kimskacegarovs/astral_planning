import numpy as np
from scipy.optimize import linear_sum_assignment
from .models import Shipment, Transport
from django.db.models import QuerySet



class PlanningOptimisationService:
    def optimal_resource_allocation(self, transports: QuerySet[Transport], shipments: QuerySet[Shipment]):
        num_transports = len(transports)
        num_orders = len(shipments)
        cost_matrix = np.zeros((num_transports, num_orders))

        for i in range(num_transports):
            for j in range(num_orders):
                cost_matrix[i][j] = self.calculate_cost(transports[i], shipments[j])

        # Use the Hungarian algorithm to find the optimal assignment.
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Create a dictionary to store the optimal allocation.
        allocation = {}
        for i, j in zip(row_indices, col_indices):
            allocation[transports[int(i)]] = shipments[int(j)]

        return allocation

    def calculate_cost(self, transport: Transport, shipment: Shipment):
        distance = CALCULATE_DISTANCE_METHOD(self, transport, shipment)
        return distance

    def calculate_distance_euclidian(self, transport: Transport, shipment: Shipment):
        transport_location = np.array(transport.location.coordinates)
        order_location = np.array(shipment.location.coordinates)
        diff = transport_location - order_location
        distance = np.linalg.norm(diff)
        return distance


CALCULATE_DISTANCE_METHOD = PlanningOptimisationService.calculate_distance_euclidian
