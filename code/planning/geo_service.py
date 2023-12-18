from .external_api import OpenStreetMapGeocodingClient, GoogleMapsClient
from .types import LocationSearchResult, RoutePolylineInput, RouteResponse


class GeoService:
    def search(self, search: str) -> list[LocationSearchResult]:
        return OpenStreetMapGeocodingClient().search(search)

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        return GoogleMapsClient().get_route(route_input=route_input)
