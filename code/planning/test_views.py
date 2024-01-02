import pytest
from .views import PlanningView, ApplyPlanningView
from .forms import CreateEntityForm, LocationSearchForm
from .types import PlanningRequest
from utils import make_request_get, make_request_post


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
    def test_post(self, shipment, transport):
        planning_request = PlanningRequest(shipment_id=shipment.id, transport_id=transport.id)
        data = {"planning_request": planning_request.as_json}
        response = make_request_post(view=ApplyPlanningView, data=data)
        assert response.status_code == 302
