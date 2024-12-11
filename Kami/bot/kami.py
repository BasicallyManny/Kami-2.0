import discord
import asyncio
from discord.ext import commands
class Kami(discord.client):
    client = commands.Bot(command_prefix='-')
    #Making sure the bot joins successfully
    @client.event
    async def on_ready():
        print('Bot is ready!')