import discord
from discord.ext import commands
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
        #All of the commands for the bot
        coordinate_commands = [
            "- **addcoord**: Save a Minecraft coordinate.",
            "- **deletecoord**: Delete a Minecraft coordinate by its name.",
            "- **clearcoords**: Clear all Minecraft coordinates for the current guild.",
            "- **find**: Search for a Minecraft coordinate by its name.",
            "- **updateName (name)**: Update the name of an already saved coordinate.",
            "- **updateCoord (name)**: Update the coordinates of an already saved coordinate.",
            "- **listcoords**: Retrieve all Minecraft coordinates for the current guild."
        ]
        
        commands_Embed=discord.Embed(
            title="**Commands**",
            color=discord.Color.green()
        )
        commands_Embed.set_author(name="Kami",icon_url=self.bot.user.avatar.url)
        #Coordinate Database Commands
        commands_Embed.add_field(name="__⚙️ Coordiante Commands__", value=("\n".join(coordinate_commands)), inline=False)
         # Add a spacer field
        commands_Embed.add_field(name="\u200b", value="\u200b", inline=False)
        #LangChain related commands
        commands_Embed.add_field(name="__🤖 AI Commands__", value=(
            "- **ask**: Ask a Minecraft-related question.\n"
            "- **clearContext**: Clear the context of the AI.\n"
            ), inline=False)    
            
        await ctx.send(embed=commands_Embed)
        
    @commands.command(name="add")
    async def add(self,ctx):
        "Add a Minecraft coordinate"

async def setup(bot):
    await bot.add_cog(MinecraftAssistantCog(bot))
