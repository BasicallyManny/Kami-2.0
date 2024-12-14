import discord  # type: ignore
import asyncio
import os
from discord.ext import commands  # type: ignore
from dotenv import load_dotenv  # type: ignore
from database.connections import MongoConnection  # Import MongoConnection

# Loading the token
load_dotenv()
DiscordToken = os.getenv("discordbotToken")

# Initialize MongoDB connection
mongo_connection = MongoConnection(os.getenv("mongoConnectionString"))  # Connect using the MongoDB URI from .env
mongo_connection.connect()  # Establish MongoDB connection

# Primary Bot function
class Kami(discord.Client):
    # Making sure the bot joins successfully
    async def on_ready(self):
        print('Bot is ready!')

    async def on_disconnect(self):
        """Called when the bot is disconnected from Discord"""
        print("Bot is disconnected")
        # Disconnect from MongoDB when the bot is disconnected
        mongo_connection.disconnect()

intents = discord.Intents.default()
intents.message_content = True

client = Kami(intents=intents)
client.run(DiscordToken)
