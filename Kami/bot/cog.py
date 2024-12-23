import discord
from discord.ext import commands
import requests # type: ignore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("apiBaseUrl", "http://127.0.0.1:8000")

class MinecraftAssistantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")
        
    @commands.command(name="help")
    async def help(self, ctx):
        'Displays general information about Kami'
        help_Embed=discord.Embed(
            description= "👾 **Your Minecraft Assistant Bot on Discord**\n\n"
                        "Kami is designed to assist with Minecraft gameplay by storing, "
                        "managing, and searching for coordinates. Additionally, it integrates AI "
                        "features powered by LangChain for Minecraft-specific questions. 🚀",
            color=discord.Color.green()
        )
        
        help_Embed.set_author(name="Kami",icon_url=self.bot.user.avatar.url)
        # Add a spacer field
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        
        help_Embed.add_field(name="🛠__Features__", value=(
            "- **Coordinate Management**: Save, search, Update, and clear Minecraft coordinates.\n"
            "- **AI Integration**: Answer Minecraft-related questions with AI.\n"
        ), inline=False)
        # Add a spacer field
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        
        help_Embed.add_field(name="__📚 How to Get Started__", value=(
            "Use the `-commands` command to see all available commands and learn how to use them."
        ), inline=False)
         # Add a spacer field
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        help_Embed.set_footer(
            text="Developed by BasicallyManny | Happy Mining! ⛏️",
        )
        
        await ctx.send(embed=help_Embed)
    
    @commands.command(name="commands")
    async def list(self,ctx):
        "List all commands"
        commands_Embed=discord.Embed(
            title="**Commands**",
            color=discord.Color.green()
        )
        commands_Embed.set_author(name="Kami",icon_url=self.bot.user.avatar.url)
        #Coordinate Database Commands
        commands_Embed.add_field(name="__⚙️ Coordiante Commands__", value=(
            "- **addcoord**: Save a Minecraft coordinate.\n"
            "- **deletecoord**: Delete a Minecraft coordinate by its name.\n"
            "- **clearcoords**: Clear all Minecraft coordinates for the current guild.\n"
            "- **find**: Search for a Minecraft coordinate by its name.\n"
            "- **updateName (name)**: update the name of a already saved coordinate.\n"
            "- **updateCoord (name)**: update the coordinates of a already saved coordinate.\n"
            "- **listcoords**: Retrieve all Minecraft coordinates for the current guild.\n"
            ), inline=False)
         # Add a spacer field
        commands_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        #LangChain related commands
        commands_Embed.add_field(name="__🤖 AI Commands__", value=(
            "- **ask**: Ask a Minecraft-related question.\n"
            "- **clearContext**: Clear the context of the AI.\n"
            ), inline=False)    
            
        await ctx.send(embed=commands_Embed)
        
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
