from database.connections import MongoConnection
import os

connection = MongoConnection(os.getenv("mongoConnectionString"))
db = connection.get_database("discord_bot")

class CoordinateModel:
    collection = db["coordinates"]

    @classmethod
    def save(cls, data):
        cls.collection.insert_one(data)

    @classmethod
    def find_by_channel(cls, guild_id, channel_id):
        return list(cls.collection.find({"guild_id": guild_id, "channel_id": channel_id}))

    @classmethod
    def delete_by_location(cls, guild_id, channel_id, location):
        result = cls.collection.delete_one({
            "guild_id": guild_id,
            "channel_id": channel_id,
            "location": location
        })
        return result.deleted_count > 0
