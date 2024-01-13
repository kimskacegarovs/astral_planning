from .external_api import OpenStreetMapGeocodingClient, GoogleMapsClient
from .types import RoutePolylineInput, RouteResponse
from .models import Location
from utils import timer
import pandas as pd
import os


class GeoService:
    @timer()
    def search(self, search: str) -> list[Location]:
        search_results = OpenStreetMapGeocodingClient().search(search=search)
        search_results = self.create_new_locations(locations=search_results)
        return search_results

    def create_new_locations(self, locations: list[Location]):
        result = []
        for location in locations:
            existing_location = Location.objects.filter(
                latitude=location.latitude, longitude=location.longitude, name=location.name
            )
            if existing_location:
                result.append(existing_location.first())
            else:
                location.save()
                result.append(location)
        return result

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        return GoogleMapsClient().get_route(route_input=route_input)

    @timer()
    def load_cities_from_file(self):
        file_name = "cities.csv"
        current_directory = os.path.dirname(os.path.realpath(__file__))
        df = pd.read_csv(os.path.join(current_directory, file_name))

        for index, row in df.iterrows():
            if Location.objects.filter(name=row["Name"]).exists():
                continue
            Location.objects.create(
                name=row["Name"],
                address=row["Name"],
                country_code=row["Country Code"],
                latitude=row["Coordinates"].split(",")[0],
                longitude=row["Coordinates"].split(",")[1],
            )
