from collections import namedtuple
import math
from typing import List


City = namedtuple('City', 'x y')
Station = namedtuple('Station', 'x y')


def euclid_distance(city: City, station: Station) -> float:
    return math.sqrt((city.x-station.x)**2 + (city.y-station.y)**2)


def quad_euclid_distance(city: City, station: Station) -> float:
    return (city.x-station.x)**2 + (city.y-station.y)**2


def error(cities: List[City], stations: List[Station], metrics) -> float:
    _sum = 0.0
    for city in cities:
        nearest = min(stations, key=lambda s: euclid_distance(city, s))
        _sum += metrics(city, nearest)
    return _sum / len(cities)


def quadratic_error(cities: List[City], stations: List[Station]) -> float:
    return error(cities, stations, quad_eudclid_distance)


def linear_error(cities: List[City], stations: List[Station]) -> float:
    return error(cities, stations, euclid_distance)
