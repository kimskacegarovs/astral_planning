import json
from dataclasses import dataclass, fields
from typing import Any
from enum import Enum
from django.db.models import QuerySet
from .models import Planning, Route, Shipment, Transport, Location


@dataclass
class PlanningSet:
    plannings: QuerySet[Planning]
    routes: QuerySet[Route]
    unplanned_transports: QuerySet[Transport]
    unplanned_shipments: QuerySet[Shipment]
    total_empty_km: float


@dataclass
class DataclassJSONMixin:
    def get_as_dict(self, json_vals=False) -> dict[str, Any]:
        fields_dict = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if json_vals:
                value = str(value)
            fields_dict[field.name] = value
        return fields_dict

    @property
    def as_dict(self) -> dict[str, Any]:
        return self.get_as_dict()

    @property
    def as_json(self) -> str:
        return json.dumps(self.get_as_dict(json_vals=True))

    @classmethod
    def from_json(cls, json_string: str):
        data = json.loads(json_string)
        valid_keys = {f.name for f in fields(cls)}  # Get attribute names of the class
        filtered_data = {key: data[key] for key in valid_keys if key in data}
        return cls(**filtered_data)


class DjangoChoicesEnum(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.value.capitalize()) for key in cls]


class EntityType(DjangoChoicesEnum):
    TRANSPORT = "transport"
    SHIPMENT = "shipment"


@dataclass
class PlanningRequest(DataclassJSONMixin):
    transport_id: str
    shipment_id: str


@dataclass
class RoutePolylineInput:
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float

    @property
    def as_tuple(self):
        return self.start_lat, self.start_lon, self.end_lat, self.end_lon


@dataclass
class RoutePolylineOutput:
    polyline_array: list[list[float, float]]


@dataclass
class RouteResponse:
    polyline: RoutePolylineOutput
    distance_km: float


@dataclass
class DataImportParsingOptions:
    location: str
    name: str
    options: list[Location]
