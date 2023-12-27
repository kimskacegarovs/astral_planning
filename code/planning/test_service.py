import pytest
from .service import PlanningService
from .models import Planning


@pytest.mark.django_db
class TestPlanningService:
    def test_cancel_planning(self, transport, shipment):
        planning = Planning.objects.create(
            transport=transport,
            shipment=shipment,
        )
        PlanningService().cancel_planning(planning_id=planning.id)
        assert Planning.objects.filter(id=planning.id).exists() is False
