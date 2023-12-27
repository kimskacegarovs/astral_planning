from unittest.mock import patch, Mock
from .geo_service import GeoService
import pytest


class TestGeoService:
    @pytest.fixture
    def geo_service(self):
        return GeoService()

    @patch("planning.external_api.OpenStreetMapGeocodingClient")
    def test_search_existing_results(self, mock_geocoding_client, geo_service):
        # Mocking the search method of OpenStreetMapGeocodingClient to return a result
        mock_geocoding_client.return_value.search.return_value = [
            Mock(display_name="Mock Location", coordinates="1.234,5.678")
        ]

        # Mocking LocationSearchResultData.objects.filter to simulate existing results
        with patch("planning.models.LocationSearchResultData.objects.filter") as mock_filter:
            mock_filter.return_value = [Mock()]

            # Perform search
            search_results = geo_service.search("Test")

            assert len(search_results) == 1  # Expecting existing results

    @patch("planning.external_api.OpenStreetMapGeocodingClient")
    def test_search_new_results(self, mock_geocoding_client, geo_service):
        # Mocking the search method of OpenStreetMapGeocodingClient to return a result
        mock_geocoding_client.return_value.search.return_value = [
            Mock(display_name="New Mock Location", coordinates="2.345,6.789")
        ]

        # Mocking LocationSearchResultData.objects.filter to simulate no existing results
        with patch("planning.models.LocationSearchResultData.objects.filter") as mock_filter:
            mock_filter.return_value = []

            # Mocking LocationSearchResultData.objects.bulk_create
            with patch("planning.models.LocationSearchResultData.objects.bulk_create") as mock_bulk_create:
                mock_bulk_create.return_value = [Mock()]

                # Perform search
                search_results = geo_service.search("Test")

                assert len(search_results) == 1  # Expecting new results
