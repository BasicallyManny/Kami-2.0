def coordinate_serializer(coordinate)->dict:
    return {
        "id": str(coordinate["_id"]),
        "guild_id": coordinate["guild_id"],
        "channel_id": coordinate["channel_id"],
        "user_id": coordinate["user_id"],
        "name": coordinate["name"],
        "x": coordinate["x"],
        "y": coordinate["y"],
        "z": coordinate["z"],
        "dimension": coordinate["dimension"],
    }

def coordinates_serializer(coordinates)->list:
    if not coordinates: 
        return []
    return [coordinate_serializer(coordinate) for coordinate in coordinates]    