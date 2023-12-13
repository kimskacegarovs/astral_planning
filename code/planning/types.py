from dataclasses import dataclass


@dataclass
class LocationSearchResult:
    display_name: str
    coordinates: str