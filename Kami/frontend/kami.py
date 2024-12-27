import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Kami.backend.config.connections import MongoConnection
import asyncio

# Add the root directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
load_dotenv()
DiscordToken = os.getenv("discordbotToken")
MongoURI = os.getenv("mongoConnectionString")

# Initialize MongoDB connection
mongo_connection = MongoConnection(MongoURI)

# Bot Class
class Kami(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=None) #disable the default help command
        
    async def on_ready(self):
        print(f"Bot is ready! Logged in as {self.user}")
        mongo_connection.connect()

    async def on_disconnect(self):
        print("Bot is disconnecting...")
        mongo_connection.disconnect()

    async def load_cogs(self):
        """Load all cogs asynchronously."""
        COG_DIRECTORY = os.path.dirname(__file__)  # Same directory as kami.py
        for filename in os.listdir(COG_DIRECTORY):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "kami.py":
                cog_name = f"bot.{filename[:-3]}"  # Update to use bot as the module prefix
                try:
                    await self.load_extension(cog_name)
                    print(f"Loaded cog: {cog_name}")
                except Exception as e:
                    print(f"Failed to load cog {cog_name}: {e}")

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize Bot
client = Kami(command_prefix="-", intents=intents) #disable the default help command

# Main Function
async def main():
    async with client:
        await client.load_cogs()
        await client.start(DiscordToken)

# Run the Bot
if __name__ == "__main__":
    asyncio.run(main())