import discord
from discord.ui import Modal, TextInput
import httpx

class FindCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Find Coordinate")

        self.name = TextInput(
            label="Coordinate Name", 
            placeholder="Enter the name of the coordinate to find", 
            style=discord.TextStyle.short, 
            required=True
        )
        
        self.add_item(self.name)
        
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        guild_id = interaction.guild.id  # Get the guild ID to identify server-specific coordinates
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8000/coordinates/{guild_id}/{name}")
                coordinates = response.json()

                if not coordinates:
                    response_embed = discord.Embed(
                        title="❌ Coordinate Not Found",
                        description=f"Could not find a coordinate named `{name}`.",
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=response_embed, ephemeral=False)
                    return

                # Pagination (For now, just Page 1/1 since pagination isn't implemented)
                total_pages = 1  # This would be dynamic if pagination is added
                response_embed = discord.Embed(
                    title=f"📌 Saved Coordinates (Page 1/{total_pages})",
                    color=discord.Color.green()
                )

                for coordinate in coordinates:
                    response_embed.add_field(
                        name=f"📌 {coordinate['coordinateName']}",
                        value=f"**Coordinates:** `{coordinate['coordinates']['x']}, {coordinate['coordinates']['y']}, {coordinate['coordinates']['z']}`\n"
                              f"**Dimension:** `{coordinate['dimension']}`\n"
                              f"**Saved by:** `{coordinate['username']}`",
                        inline=False
                    )

                await interaction.response.send_message(embed=response_embed, ephemeral=False)

        except Exception as e:
            error_embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: `{str(e)}`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
