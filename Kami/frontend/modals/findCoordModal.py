import discord
from discord.ui import Modal, TextInput
import httpx

class FindCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Find Coordinate")

        self.name = TextInput(
            label="Name", 
            placeholder="Enter a name for the coordinate you are looking for 🔍", 
            style=discord.TextStyle.short, 
            required=True
        )
        
        async def on_submit(self, interaction: discord.Interaction):
            name = self.name.value
            guild_id = interaction.guild.id  # Get the guild ID to identify server-specific coordinates
            await interaction.response.defer()  # Prevent timeout while fetching data
            #send GET request to FastAPI endpoint
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f"http://localhost:8000/coordinates/{guild_id}/{name}")

                # Check response from FastAPI
                if response.status_code == 200:
                    coordinates = response.json()
                    if not coordinates:
                        response_embed = discord.Embed(
                            title="❌ Coordinate Not Found",
                            description=f"Could not find a coordinate named `{name}`.",
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=response_embed, ephemeral=True)
                    
                    #Return all coordinates with the same name:
                    response_embed = discord.Embed(
                        title="✅ Coordinate Found",        
                        description=    f"Coordinate `{name}` was found successfully.",
                        color=discord.Color.green()
                    ) 
                    for coordinate in coordinates:
                        response_embed.add_field(
                            name=f"📌{coordinate['name']}",
                            value=f"**Coordinates: **{coordinate['x']} Y: {coordinate['y']} Z: {coordinate['z']}",
                            inline=False
                        )    
                    await interaction.response.send_message(embed=response_embed, ephemeral=True)
                
                #Error handling
                elif response.status_code == 404:
                    response_embed = discord.Embed(
                        title="❌ Coordinate Not Found",
                        description=f"Could not find a coordinate named `{name}`.",
                        color=discord.Color.red()
                    )
                else:
                    response_embed = discord.Embed(
                        title="⚠️ Coordinate Not Found",
                        description="An error occurred while trying to find the coordinate. Please try again.",
                        color=discord.Color.orange()
                    )
                await interaction.response.send_message(embed=response_embed, ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"An error occurred: {str(e)}", ephemeral=True)
        
