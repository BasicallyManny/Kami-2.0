import discord
from discord.ui import Modal, TextInput
import httpx

class DelCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Delete Coordinate")

        self.name = TextInput(
            label="Coordinate Name", 
            placeholder="Enter the name of the coordinate to remove", 
            style=discord.TextStyle.short, 
            required=True
        )
        
        self.add_item(self.name)
        
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        guild_id = interaction.guild.id  # Get the guild ID to identify server-specific coordinates
        
        # Send DELETE request to FastAPI endpoint
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"http://localhost:8000/coordinates/{guild_id}/{name}"
                )

            # Check response from FastAPI
            if response.status_code == 200:
                response_embed = discord.Embed(
                    title="🗑️ Coordinate Deleted",
                    description=f"Coordinate `{name}` was removed successfully.",
                    color=discord.Color.green()
                )
            elif response.status_code == 404:
                response_embed = discord.Embed(
                    title="❌ Coordinate Not Found",
                    description=f"Could not find a coordinate named `{name}`.",
                    color=discord.Color.red()
                )
            else:
                response_embed = discord.Embed(
                    title="⚠️ Deletion Failed",
                    description="An error occurred while trying to delete the coordinate. Please try again.",
                    color=discord.Color.orange()
                )

        except Exception as e:
            response_embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )

        # Send the response message
        await interaction.response.send_message(embed=response_embed, ephemeral=False)
