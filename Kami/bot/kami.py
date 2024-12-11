import discord # type: ignore
import asyncio
import os
from discord.ext import commands # type: ignore
from dotenv import load_dotenv # type: ignore 

#Loading the token
load_dotenv()
DiscordToken = os.getenv("discordbotToken")

#Primary Bot function
class Kami(discord.Client):
    #Making sure the bot joins successfully
    async def on_ready(self):
        print('Bot is ready!')


intents = discord.Intents.default()
intents.message_content = True

client = Kami(intents=intents)
client.run(DiscordToken)
