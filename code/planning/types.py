from dataclasses import dataclass
from enum import Enum
import json


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
        return cls(**json.loads(json_string))