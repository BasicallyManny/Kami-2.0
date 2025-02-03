def coordinate_serializer(coordinate: dict) -> dict:
    return {
        "id": str(coordinate.get("_id", "")),  # Ensure `_id` is handled
        "guild_id": coordinate.get("guild_id"),
        "channel_id": coordinate.get("channel_id"),
        "user_id": coordinate.get("user_id"),
        "username": coordinate.get("username"),
        "avatar_url": coordinate.get("avatar_url"),
        "dimension": coordinate.get("dimension"),  # Corrected from "world" to match model field
        "coordinates": {
            "x": coordinate.get("coordinates", {}).get("x"),
            "y": coordinate.get("coordinates", {}).get("y"),
            "z": coordinate.get("coordinates", {}).get("z")
        },
        "description": coordinate.get("description"),
        "created_at": coordinate.get("created_at", None),  # Handle missing timestamps
    }


def user_serializer(user: dict) -> dict:
    return {
        "id": str(user.get("_id", "")),  # Ensure `_id` is handled
        "username": user.get("username"),
        "avatar_url": user.get("avatar_url"),
        "joined_servers": user.get("joined_servers", []),  # Include joined_servers as list if needed
    }

    
def server_serializer(server: dict) -> dict:
    return {
        "id": str(server.get("_id", "")),  # Ensure `_id` is handled
        "guild_id": server.get("guild_id"),
        "channel_id": server.get("channel_id"),
        "logining_channel_id": server.get("logining_channel_id"),
    }


