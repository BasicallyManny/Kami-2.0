import discord
from discord.ext import commands
import asyncio

class CoordCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.coord_list = {}

    async def get_user_input(self, ctx, prompt: str, timeout: float) -> str:
        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        await ctx.send(prompt)
        try:
            msg = await self.bot.wait_for("message", check=check, timeout=timeout)
            return msg.content
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                description="Sorry, you didn't respond in time.",
                color=discord.Color.dark_red()
            ))
            return None

    async def find_coord(self, ctx, name: str):
        if name in self.coord_list:
            return self.coord_list[name]
        await ctx.send(embed=discord.Embed(
            description=f"Sorry, '{name}' could not be found.",
            color=discord.Color.dark_red()
        ))
        return None

    @commands.command(name="add", description="Add coordinates to the list")
    async def add_coord(self, ctx):
        name = await self.get_user_input(ctx, "What have you found?", timeout=30)
        if not name:
            return
        x = await self.get_user_input(ctx, "Enter the X coordinate:", timeout=30)
        y = await self.get_user_input(ctx, "Enter the Y coordinate:", timeout=30)
        z = await self.get_user_input(ctx, "Enter the Z coordinate:", timeout=30)
        if None in (x, y, z):
            return

        if name in self.coord_list:
            await ctx.send("Coordinates with this name already exist. Try again.")
        else:
            self.coord_list[name] = f"[{x}, {y}, {z}]"
            await ctx.send(embed=discord.Embed(
                title="Coordinates Added",
                description=f"{name}: [{x}, {y}, {z}]",
                color=discord.Color.green()
            ))

    @commands.command(name="search", description="Search for saved coordinates")
    async def search_coord(self, ctx):
        name = await self.get_user_input(ctx, "Enter the name to search for:", timeout=30)
        if not name:
            return
        result = await self.find_coord(ctx, name)
        if result:
            await ctx.send(embed=discord.Embed(
                title=f"Coordinates for {name}",
                description=result,
                color=discord.Color.green()
            ))

    @commands.command(name="list", description="List all saved coordinates")
    async def list_coords(self, ctx):
        if not self.coord_list:
            await ctx.send("No coordinates saved yet.")
        else:
            formatted = "\n".join([f"{name}: {coords}" for name, coords in self.coord_list.items()])
            await ctx.send(embed=discord.Embed(
                title="Saved Coordinates",
                description=formatted,
                color=discord.Color.green()
            ))

    @commands.command(name="remove", description="Remove a specific coordinate")
    async def remove_coord(self, ctx):
        name = await self.get_user_input(ctx, "Enter the name to remove:", timeout=30)
        if not name:
            return
        if name in self.coord_list:
            del self.coord_list[name]
            await ctx.send(embed=discord.Embed(
                description=f"Removed '{name}' from the list.",
                color=discord.Color.red()
            ))
        else:
            await ctx.send(f"No coordinates found for '{name}'.")

    @commands.command(name="clear", description="Clear all saved coordinates")
    async def clear_coords(self, ctx):
        self.coord_list.clear()
        await ctx.send(embed=discord.Embed(
            description="All coordinates have been cleared.",
            color=discord.Color.red()
        ))

# Cog Setup Function
async def setup(bot):
    await bot.add_cog(CoordCommands(bot))
