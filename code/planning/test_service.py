import pytest
from .service import PlanningService
from .models import Transport, Shipment, Planning


@pytest.fixture
def transport():
    return Transport.objects.create(name="Test Transport")


@pytest.fixture
def shipment():
    return Shipment.objects.create(name="Test Shipment")


@pytest.mark.django_db
class TestPlanningService:
    def test_cancel_planning(self, transport, shipment):
        planning = Planning.objects.create(
            transport=transport,
            shipment=shipment,
        )
        PlanningService().cancel_planning(planning_id=planning.id)
        assert Planning.objects.filter(id=planning.id).exists() is False
