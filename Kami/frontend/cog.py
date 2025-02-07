import asyncio
import discord
from discord.ext import commands
from discord import app_commands

from modals.addCoordModal import AddCoordModal
from modals.delCoordModal import DelCoordModal 
from modals.findCoordModal import FindCoordModal

import httpx

# Define the Minecraft Assistant Cog
class MinecraftAssistantCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")
        
    @commands.command(name="help") 
    async def help(self, ctx):
        'Displays general information about Kami'
        help_Embed = discord.Embed(
            description= "👾 **Your Minecraft Assistant Bot on Discord**\n\n"
                        "Kami is designed to assist with Minecraft gameplay by storing, "
                        "managing, and searching for coordinates. Additionally, it integrates AI "
                        "features powered by LangChain for Minecraft-specific questions. 🚀",
            color=discord.Color.green()
        )
        
        help_Embed.set_author(name="Kami", icon_url=self.bot.user.avatar.url)
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        help_Embed.add_field(name="🛠__Features__", value=( 
            "- **Coordinate Management**: Save, search, update, and clear Minecraft coordinates.\n"
            "- **AI Integration**: Answer Minecraft-related questions with AI.\n"
        ), inline=False)
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        help_Embed.add_field(name="__📚 How to Get Started__", value=( 
            "Use the `-commands` command to see all available commands and learn how to use them."
        ), inline=False)
        help_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        help_Embed.set_footer(
            text="Developed by BasicallyManny | Happy Mining! ⛏️",
        )
        
        await ctx.send(embed=help_Embed)
    
    @commands.command(name="commands")
    async def commands(self, ctx):
        "List all commands"
        coordinate_commands = [
            "- **/addcoord**: Save a Minecraft coordinate.",
            "- **/deletecoord**: Delete a Minecraft coordinate by its name.",
            "- **/clearcoords**: Clear all Minecraft coordinates for the current guild.",
            "- **/find**: Search for a Minecraft coordinate by its name.",
            "- **/updateName (name)**: Update the name of an already saved coordinate.",
            "- **/updateCoord (name)**: Update the coordinates of an already saved coordinate.",
            "- **/listcoords**: Retrieve all Minecraft coordinates for the current guild."
        ]
        
        commands_Embed = discord.Embed(
            title="**Commands**",
            color=discord.Color.green()
        )
        commands_Embed.set_author(name="Kami", icon_url=self.bot.user.avatar.url)
        commands_Embed.add_field(name="__⚙️ Coordinate Commands__", value="\n".join(coordinate_commands), inline=False)
        commands_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        commands_Embed.add_field(name="__🤖 AI Commands__", value=( 
            "- **ask**: Ask a Minecraft-related question.\n"
            "- **clearContext**: Clear the context of the AI.\n"
            ), inline=False)    
            
        await ctx.send(embed=commands_Embed)
    
    @app_commands.command(name="addcoord", description="Add a Minecraft coordinate using a modal")
    async def add_coord(self, interaction: discord.Interaction):
        """
        Add a Minecraft coordinate using a modal
        """
        try:
            await interaction.response.send_modal(AddCoordModal())
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="deletecoord", description="Remove a Minecraft coordinate using a modal")
    async def del_coord(self, interaction: discord.Interaction):
        """
        Remove a Minecraft coordinate using a modal
        """
        try:
            await interaction.response.send_modal(DelCoordModal())
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="clearcoords", description="Clear all Minecraft coordinates for the current guild")
    async def clear_coords(self, interaction: discord.Interaction):
        """
        Clear all Minecraft coordinates for the current guild
        """
        await interaction.response.defer()  # Defer response to prevent timeout

        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(f"http://localhost:8000/coordinates/{interaction.guild.id}")

            # Check Response from FastAPI
            if response.status_code == 200:
                response_embed = discord.Embed(
                    title="🗑️ Coordinates Cleared",
                    description="All Minecraft coordinates for this server have been successfully deleted.",
                    color=discord.Color.green()
                )
            elif response.status_code == 404:
                response_embed = discord.Embed(
                    title="❌ No Coordinates Saved",
                    description="No coordinates were found for this server.",
                    color=discord.Color.red()
                )
            else:
                response_embed = discord.Embed(
                    title="⚠️ Deletion Failed",
                    description="An error occurred while trying to delete the coordinates. Please try again.",
                    color=discord.Color.orange()
                )

        except Exception as e:
            response_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=response_embed)
    
    @app_commands.command(name="listcoords", description="List all Minecraft coordinates for the current guild")
    async def list_coords(self, interaction: discord.Interaction):
        """
        List all Minecraft coordinates for the current guild with pagination and sorting.
        """
        await interaction.response.defer()  # Prevent timeout while fetching data

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8000/coordinates/{interaction.guild.id}")

            if response.status_code == 200:
                coordinates = response.json()

                if not coordinates:
                    response_embed = discord.Embed(
                        title="❌ No Coordinates Saved",
                        description="There are no saved coordinates for this server.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=response_embed)
                    return

                # Sort by dimension
                coordinates.sort(key=lambda c: c.get("dimension", ""))

                # Pagination setup
                MAX_COORDS_PER_PAGE=5
                total_pages = (len(coordinates) // MAX_COORDS_PER_PAGE) + (1 if len(coordinates) % MAX_COORDS_PER_PAGE > 0 else 0)
                current_page = 0

                async def generate_embed(page: int):
                    """Creates an embed for the given page index."""
                    start = page * MAX_COORDS_PER_PAGE
                    end = start + MAX_COORDS_PER_PAGE
                    coords_page = coordinates[start:end]

                    embed = discord.Embed(
                        title=f"Saved Coordinates (Page {page+1}/{total_pages})",
                        color=discord.Color.green()
                    )

                    for coord in coords_page:
                        name = coord.get("coordinateName", "Unknown Name")
                        coords = coord.get("coordinates", "Unknown Coordinates")
                        dimension = coord.get("dimension", "Unknown Dimension")
                        username = coord.get("username", "Unknown User")
                        
                        #format the coords
                        coords = f"{coords.get('x', 'Unknown')},{coords.get('y', 'Unknown')},{coords.get('z', 'Unknown')}"
                        embed.add_field(
                            name=f"📌**{name}**",
                            value=f"**Coordinates: **{coords}\n**Dimension:** {dimension}\n**Saved by: {username}**" ,
                            inline=False
                        )

                    return embed

                # Send first page
                message = await interaction.followup.send(embed=await generate_embed(current_page))

                # If only one page, no need for reactions
                if total_pages == 1:
                    return

                # Add pagination reactions
                await message.add_reaction("⬅️")
                await message.add_reaction("➡️")

                def check(reaction, user):
                    return user == interaction.user and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]
                #listen for reactions
                while True:
                    try:
                        reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                        if str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                            current_page += 1
                        elif str(reaction.emoji) == "⬅️" and current_page > 0:
                            current_page -= 1

                        await message.edit(embed=await generate_embed(current_page))
                        await message.remove_reaction(reaction, user)

                    except asyncio.TimeoutError:
                        break  # Exit loop if user is inactive

        except Exception as e:
            print(f"❌ Error fetching coordinates: {str(e)}")  # Debugging log
            response_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=response_embed)

    @app_commands.command(name="find", description="Delete all Minecraft coordinates for the current guild")
    async def find_coords(self, interaction: discord.Interaction):
        """Look for a saved coordinates using a modal"""
        try:
            await interaction.response.send_modal(FindCoordModal())
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
# Setup function for loading the cog
async def setup(bot):
    await bot.add_cog(MinecraftAssistantCog(bot))

