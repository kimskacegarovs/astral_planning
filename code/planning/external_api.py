import requests
from planning.types import LocationSearchResult, RoutePolylineInput, RoutePolylineOutput
import openrouteservice
import numpy as np


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
                coordinates=f"{result['lat']}, {result['lon']}"
            )
            for result in response.json()
        ]
        return results


class OpenRouteService:
    API_KEY = "5b3ce3597851110001cf62481cb7eedbdd5649a896773031a3489e53"

    def __init__(self):
        self.client: openrouteservice.Client = openrouteservice.Client(key=self.API_KEY)

    def get_directions(self, route_input: RoutePolylineInput) -> dict:
        start_lat, start_lon, end_lat, end_lon = route_input.as_tuple
        payload_tuple = ((start_lon, start_lat), (end_lon, end_lat))
        # Note that lon comes first in the tuple for OpenRouteService!
        routes = self.client.directions(payload_tuple)
        return routes

    def get_polyline_array(self, data) -> RoutePolylineOutput:
        geometry = data['routes'][0]['geometry']
        polyline_coords = openrouteservice.convert.decode_polyline(geometry)["coordinates"]

        # swap lat and lon using numpy
        polyline_coords = np.array(polyline_coords)
        polyline_coords[:, [0, 1]] = polyline_coords[:, [1, 0]]
        polyline_coords = polyline_coords.tolist()

        return polyline_coords

    def get_route_polyline(self, route_input: RoutePolylineInput) -> RoutePolylineOutput:
        directions = self.get_directions(route_input)
        polyline = self.get_polyline_array(directions)
        return polyline
