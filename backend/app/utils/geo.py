from math import atan2, cos, radians, sin, sqrt


EARTH_RADIUS_KM = 6371.0
KM_PER_DEGREE_LATITUDE = 111.32


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Calculate Haversine distance between two WGS84 points."""
    lat1_rad, lat2_rad = radians(lat1), radians(lat2)
    delta_lat, delta_lon = radians(lat2 - lat1), radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
    )
    return EARTH_RADIUS_KM * 2 * atan2(sqrt(a), sqrt(1 - a))


def radius_to_latitude_degrees(radius_km: float) -> float:
    return radius_km / KM_PER_DEGREE_LATITUDE
