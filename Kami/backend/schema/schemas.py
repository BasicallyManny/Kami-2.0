def coordinate_serializer(coordinate: dict) -> dict:
    return {
        "id": str(coordinate.get("_id", "")),  # Ensure `_id` is handled
        "guild_id": coordinate.get("guild_id"),
        "channel_id": coordinate.get("channel_id"),
        "user_id": coordinate.get("user_id"),
        "name": coordinate.get("name"),
        "x": coordinate.get("x"),
        "y": coordinate.get("y"),
        "z": coordinate.get("z"),
        "dimension": coordinate.get("dimension"),
        "created_at": coordinate.get("created_at", None),  # Handle missing timestamps
    }

def coordinates_serializer(coordinates) -> list:
    return [coordinate_serializer(coordinate) for coordinate in coordinates or []]
