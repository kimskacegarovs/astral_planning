import os

import googlemaps
import numpy as np
import polyline
import requests
from dotenv import load_dotenv
from planning.types import LocationSearchResult, RoutePolylineInput, RouteResponse

load_dotenv()


class OpenStreetMapGeocodingClient:
    BASE_URL = "https://nominatim.openstreetmap.org"

    def search(self, search: str) -> list[LocationSearchResult]:
        url = f"{self.BASE_URL}/search"
        params = {"format": "json", "q": search}
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = []
        for r in response.json():
            location = LocationSearchResult(display_name=r["display_name"], coordinates=f"{r['lat']}, {r['lon']}")
            results.append(location)
        return results


class GoogleMapsClient:
    API_KEY = os.getenv("API_KEY_GOOGLE_MAPS")  # TODO Move to settings

    def __init__(self):
        self.client = googlemaps.Client(key=self.API_KEY)

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        directions = self.client.directions(
            origin=(route_input.start_lat, route_input.start_lon),
            destination=(route_input.end_lat, route_input.end_lon),
        )

        polyline_points = directions[0]["overview_polyline"]["points"]
        route_coordinates = polyline.decode(polyline_points)
        route_polyline = np.array(route_coordinates).tolist()

        total_distance_meters = directions[0]["legs"][0]["distance"]["value"]
        total_distance_km = round(total_distance_meters / 1000)

        return RouteResponse(polyline=route_polyline, distance_km=total_distance_km)
