from dataclasses import dataclass
import json


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