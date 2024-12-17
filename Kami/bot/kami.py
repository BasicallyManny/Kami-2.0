import os
import sys
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database.connections import MongoConnection

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
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def on_ready(self):
        print(f"Bot is ready! Logged in as {self.user}")
        mongo_connection.connect()

    async def on_disconnect(self):
        print("Bot is disconnecting...")
        mongo_connection.disconnect()

    async def load_cogs(self):
        """Load all cogs asynchronously."""
        COG_DIRECTORY = os.path.join(os.path.dirname(__file__), "cogs")
        for filename in os.listdir(COG_DIRECTORY):
            if filename.endswith(".py") and filename != "__init__.py":
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.load_extension(cog_name)
                    print(f"Loaded cog: {cog_name}")
                except Exception as e:
                    print(f"Failed to load cog {cog_name}: {e}")

# Bot Intents
intents = discord.Intents.default()
intents.message_content = True

# Initialize Bot
client = Kami(command_prefix="-", intents=intents)

# Main Function
async def main():
    async with client:
        await client.load_cogs()
        await client.start(DiscordToken)

# Run the Bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
