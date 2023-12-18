from .external_api import OpenStreetMapGeocodingClient, GoogleMapsClient
from django.db.models import QuerySet
from .types import RoutePolylineInput, RouteResponse
from .models import LocationSearchResultData
from utils import timer


class GeoService:
    @timer()
    def search(self, search: str) -> QuerySet[LocationSearchResultData]:
        if existing_results := LocationSearchResultData.objects.filter(search_text=search):
            print(f"Found {len(existing_results)} existing results for search '{search}'")
            return existing_results

        new_results = LocationSearchResultData.objects.bulk_create(
            [
                LocationSearchResultData(
                    search_text=search,
                    display_name=result.display_name,
                    coordinates=result.coordinates,
                )
                for result in OpenStreetMapGeocodingClient().search(search)
            ]
        )
        return new_results

    def get_route(self, route_input: RoutePolylineInput) -> RouteResponse:
        return GoogleMapsClient().get_route(route_input=route_input)
