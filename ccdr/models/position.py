from dataclasses import dataclass


@dataclass
class Coordinates:
    latitude: float
    longitude: float


@dataclass
class Position:
    address: str
    coordinates: Coordinates
    city: str  # <- can get City from city_code
    nut_iii: str  # <- can get from City?
