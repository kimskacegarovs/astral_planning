from .external_api import OpenStreetMapGeocodingClient, GoogleMapsClient
from .types import RoutePolylineInput, RouteResponse
from .models import Location
from utils import timer


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
