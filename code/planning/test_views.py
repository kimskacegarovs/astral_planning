import pytest
from unittest.mock import patch
from .models import Planning
from .views import (
    LandingView,
    PlanningView,
    ApplyPlanningView,
    ResetPlanningView,
    CancelPlanningView,
    LocationSearchView,
    LocationSearchResultSelectView,
)
from .forms import CreateEntityForm, LocationSearchForm
from .types import PlanningRequest
from utils import make_request_get, make_request_post
import json


@pytest.mark.django_db
class TestLandingView:
    def test_get(self):
        response = make_request_get(LandingView)
        assert response.status_code == 200


@pytest.mark.django_db
class TestPlanningView:
    def test_get_context_data(self):
        response = make_request_get(PlanningView)
        assert response.status_code == 200  # Ensure the response is successful

        # Check if necessary context data is present in the response
        assert "apply_planning_url" in response.context_data
        assert "location_form" in response.context_data
        assert "location_search_form" in response.context_data

        # Verify the values of context data
        assert isinstance(response.context_data["location_form"], CreateEntityForm)
        assert isinstance(response.context_data["location_search_form"], LocationSearchForm)


@pytest.mark.django_db
class TestApplyPlanningView:
    def test_post(self, shipment, transport, route):
        planning_request = PlanningRequest(shipment_id=shipment.id, transport_id=transport.id)
        data = {"planning_request": planning_request.as_json}
        with patch("planning.service.PlanningService.get_route", return_value=route):
            response = make_request_post(view=ApplyPlanningView, data=data)
        assert response.status_code == 302
        assert transport.planned_shipment is not None


@pytest.mark.django_db
class TestResetPlanningView:
    def test_post(self, planning):
        response = make_request_post(view=ResetPlanningView, data={})
        assert response.status_code == 302
        assert Planning.objects.all().exists() is False


@pytest.mark.django_db
class TestCancelPlanningView:
    def test_post(self, planning):
        response = make_request_post(view=CancelPlanningView, data={"planning_id": planning.id})
        assert response.status_code == 302
        assert Planning.objects.all().exists() is False


@pytest.mark.django_db
class TestLocationSearchView:
    def test_post(self, location_search_result_data):
        form = LocationSearchForm(data={"search": "Amsterdam"})
        return_value = location_search_result_data
        with patch("planning.geo_service.GeoService.search", return_value=[return_value]):
            response = make_request_post(view=LocationSearchView, data=form.data)
        assert response.status_code == 200
        assert return_value.name in response.content.decode("utf-8")


@pytest.mark.django_db
class TestLocationSearchResultSelectView:
    def test_post(self, location_search_result_data):
        form = LocationSearchForm(data={"search": "Amsterdam"})
        form_data = json.dumps(form.data)
        data = location_search_result_data.as_json
        response = make_request_post(view=LocationSearchResultSelectView, data={"data": form_data, "result": data})
        assert response.status_code == 200
        assert location_search_result_data.name in response.content.decode("utf-8")
