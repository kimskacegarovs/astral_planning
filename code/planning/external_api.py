import os

import googlemaps
import numpy as np
import polyline
import requests
from dotenv import load_dotenv
from .models import Location
from planning.types import RoutePolylineInput, RouteResponse
from utils import is_pytest

load_dotenv()


class OpenStreetMapGeocodingClient:
    BASE_URL = "https://nominatim.openstreetmap.org"

    def get_location_name(self, address: dict) -> str:
        location_name = None
        if town := address.get("town"):
            location_name = town
        elif city := address.get("city"):
            location_name = city
        return location_name

    def get_postcode(self, country_code: str, address: dict) -> str:
        postcode_full = None
        if postcode := address.get("postcode"):
            postcode_full = f"{country_code}-{postcode}" if postcode.isdigit() else postcode
        return postcode_full

    def search(self, search: str) -> list[Location]:
        url = f"{self.BASE_URL}/search"
        params = {"format": "json", "q": search, "addressdetails": 1, "limit": 5}
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = []

        for r in response.json():
            country_code = r["address"]["country_code"].upper()

            location = Location(
                name=r["name"],
                country_code=country_code,
                address=self.get_location_name(address=r["address"]),
                postcode=self.get_postcode(country_code=country_code, address=r["address"]),
                latitude=r["lat"],
                longitude=r["lon"],
            )
            results.append(location)
        return results


class GoogleMapsClient:
    def __init__(self):
        api_key = os.getenv("API_KEY_GOOGLE_MAPS") if not is_pytest() else None  # TODO Make this logic more generic
        self.client = googlemaps.Client(key=api_key)

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
