import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("apiBaseUrl", "http://127.0.0.1:8000")

class MinecraftAssistantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="addcoord")
    async def add_coordinate(self, ctx, x: int, y: int, z: int, *, description: str):
        """Command to add a Minecraft coordinate to the database."""
        payload = {
            "guild_id": ctx.guild.id,
            "channel_id": ctx.channel.id,
            "user_id": ctx.author.id,
            "x": x,
            "y": y,
            "z": z,
            "description": description,
        }

        try:
            response = requests.post(f"{API_URL}/coordinates/", json=payload)
            if response.status_code == 200:
                data = response.json()
                await ctx.send(
                    f"Coordinate saved successfully! ID: `{data['id']}`\nDescription: {description}"
                )
            else:
                await ctx.send(
                    "Failed to save coordinate. Please try again later."
                )
        except requests.RequestException as e:
            await ctx.send(f"An error occurred while connecting to the backend: {e}")

    @commands.command(name="listcoords")
    async def list_coordinates(self, ctx):
        """Retrieve all Minecraft coordinates for the current guild."""
        try:
            response = requests.get(f"{API_URL}/coordinates/?guild_id={ctx.guild.id}")
            if response.status_code == 200:
                coordinates = response.json()
                if coordinates:
                    embed = discord.Embed(
                        title=f"Coordinates for {ctx.guild.name}",
                        color=discord.Color.green(),
                    )
                    for coord in coordinates:
                        embed.add_field(
                            name=f"({coord['x']}, {coord['y']}, {coord['z']})",
                            value=coord['description'],
                            inline=False,
                        )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No coordinates found for this server.")
            else:
                await ctx.send("Failed to retrieve coordinates. Please try again later.")
        except requests.RequestException as e:
            await ctx.send(f"An error occurred while connecting to the backend: {e}")

    @commands.command(name="deletecoord")
    async def delete_coordinate(self, ctx, coord_id: str):
        """Delete a Minecraft coordinate by its ID."""
        try:
            response = requests.delete(f"{API_URL}/coordinates/{coord_id}")
            if response.status_code == 200:
                await ctx.send(f"Successfully deleted coordinate with ID: `{coord_id}`")
            else:
                await ctx.send("Failed to delete coordinate. Ensure the ID is correct.")
        except requests.RequestException as e:
            await ctx.send(f"An error occurred while connecting to the backend: {e}")

async def setup(bot):
    await bot.add_cog(MinecraftAssistantCog(bot))
