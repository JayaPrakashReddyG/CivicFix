
def validate_location(latitude, longitude):
    if latitude in (None, "") and longitude in (None, ""):
        return None, None

    if latitude in (None, "") or longitude in (None, ""):
        raise ValueError(
            "Both latitude and longitude are required"
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        raise ValueError("Latitude and longitude must be numbers")

    if not (-90 <= latitude <= 90):
        raise ValueError("Latitude must be between -90 and 90")

    if not (-180 <= longitude <= 180):
        raise ValueError("Longitude must be between -180 and 180")

    return latitude, longitude
