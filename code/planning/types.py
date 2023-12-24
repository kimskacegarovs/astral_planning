import json
from dataclasses import dataclass, fields
from enum import Enum


class DjangoChoicesEnum(Enum):
    @classmethod
    def choices(cls):
        return [(key.value, key.value.capitalize()) for key in cls]


class EntityType(DjangoChoicesEnum):
    TRANSPORT = "transport"
    SHIPMENT = "shipment"


@dataclass
class LocationSearchResult:
    display_name: str
    coordinates: str

    @property
    def as_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        valid_keys = {f.name for f in fields(cls)}  # Get attribute names of the class
        filtered_data = {key: data[key] for key in valid_keys if key in data}
        return cls(**filtered_data)


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
    polyline_array = list[list[float, float]]


@dataclass
class RouteResponse:
    polyline: RoutePolylineOutput
    distance_km: float


@dataclass
class DataImportParsingOptions:
    location: str
    name: str
    options: list[LocationSearchResult]
