import discord
from discord.ext import commands
from discord import app_commands

import os
from dotenv import load_dotenv
from modals.addCoordModal import AddCoordModal
from modals.delCoordModal import DelCoordModal 

# Load environment variables
load_dotenv()
API_URL = os.getenv("apiBaseUrl", "http://127.0.0.1:8000")

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
    async def list(self, ctx):
        "List all commands"
        coordinate_commands = [
            "- **/addcoord**: Save a Minecraft coordinate.",
            "- **/deletecoord**: Delete a Minecraft coordinate by its name.",
            "- **-clearcoords**: Clear all Minecraft coordinates for the current guild.",
            "- **-find**: Search for a Minecraft coordinate by its name.",
            "- **/updateName (name)**: Update the name of an already saved coordinate.",
            "- **/updateCoord (name)**: Update the coordinates of an already saved coordinate.",
            "- **-listcoords**: Retrieve all Minecraft coordinates for the current guild."
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
        


# Setup function for loading the cog
async def setup(bot):
    await bot.add_cog(MinecraftAssistantCog(bot))

