import os

import numpy as np
import openrouteservice
import requests
from dotenv import load_dotenv
from planning.types import LocationSearchResult, RoutePolylineInput, RoutePolylineOutput, RouteResponse

load_dotenv()


class OpenStreetMapGeocodingService:
    BASE_URL = "https://nominatim.openstreetmap.org"

    def search(self, search: str) -> list[LocationSearchResult]:
        url = f"{self.BASE_URL}/search"
        params = {"format": "json", "q": search}
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = [
            LocationSearchResult(
                display_name=result["display_name"],
                coordinates=f"{result['lat']}, {result['lon']}",
            )
            for result in response.json()
        ]
        return results


class OpenRouteService:
    API_KEY = os.getenv("API_KEY_OPEN_ROUTE_SERVICE")  # TODO Move to settings
    DISTANCE_UNIT = "km"
    # BASE_URL_LOCAL = "http://localhost:8080/ors"
    BASE_URL_LOCAL = "https://api.openrouteservice.org/"

    def __init__(self):
        self.client: openrouteservice.Client = openrouteservice.Client(key=self.API_KEY, base_url=self.BASE_URL_LOCAL)

    def get_payload_tuple(self, route_input: RoutePolylineInput) -> tuple:
        start_lat, start_lon, end_lat, end_lon = route_input.as_tuple
        # Note that lon comes first in the tuple for OpenRouteService!
        payload_tuple = ((start_lon, start_lat), (end_lon, end_lat))
        return payload_tuple

    def get_directions(self, route_input: RoutePolylineInput) -> dict:
        payload_tuple = self.get_payload_tuple(route_input)
        routes = self.client.directions(payload_tuple, instructions=False, units=self.DISTANCE_UNIT)
        return routes

    def get_polyline_array(self, data) -> RoutePolylineOutput:
        geometry = data["routes"][0]["geometry"]
        polyline_coords = openrouteservice.convert.decode_polyline(geometry)["coordinates"]

        # swap lat and lon using numpy
        polyline_coords = np.array(polyline_coords)
        polyline_coords[:, [0, 1]] = polyline_coords[:, [1, 0]]
        polyline_coords = polyline_coords.tolist()

        return polyline_coords

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        directions = self.get_directions(route_input)
        polyline = self.get_polyline_array(directions)
        distance_km = round(directions["routes"][0]["summary"]["distance"])
        return RouteResponse(polyline=polyline, distance_km=distance_km)
