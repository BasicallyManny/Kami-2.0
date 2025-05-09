import os
from dotenv import load_dotenv

import discord
from discord.ui import Modal, TextInput
import httpx
from views.coordinateSelectView import CoordinateSelectView

class DelCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Delete Coordinate")
        
        load_dotenv()
        self.API_URL = os.getenv('API_URL')
        
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
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.API_URL}/coordinates/{guild_id}/{name}")
                coordinates = response.json()

                # Handle error from API
                if isinstance(coordinates, dict) and coordinates.get("detail") == '404: Coordinate Name not found':
                    response_embed = discord.Embed(
                        title="❌ Coordinate Not Found",
                        description=f"Could not find a coordinate named `{name}`.",
                        color=discord.Color.red()
                    )   
                    await interaction.response.send_message(embed=response_embed, ephemeral=True)
                    return
                
                if len(coordinates) == 1:
                    # Only one coordinate found, delete it directly
                    async with httpx.AsyncClient() as client:
                        response = await client.delete(
                            f"{self.API_URL}/coordinates/{coordinates[0]['guild_id']}/{coordinates[0]['coordinateName']}"
                        )

                    if response.status_code == 200:
                        response_embed = discord.Embed(
                            title="✅ Coordinate Deleted",
                            description=f"Coordinate `{coordinates[0]['coordinateName']}` has been successfully deleted!",
                            color=discord.Color.green()
                        )
                    else:
                        error_message = response.json().get("detail", "Unknown error")
                        response_embed = discord.Embed(
                            title="⚠️ Error Deleting Coordinate",
                            description=f"Error: {error_message}",
                            color=discord.Color.red()
                        )    
                    await interaction.response.send_message(embed=response_embed, ephemeral=False)
                    return
                # Ensure data is valid
                if not isinstance(coordinates, list) or not all(isinstance(coord, dict) for coord in coordinates):
                    await interaction.response.send_message("⚠️ Error: Coordinate data is not in the correct format.", ephemeral=True)
                    return

                # Create the CoordinateSelectView
                select_view = CoordinateSelectView(
                    coordinates=coordinates,
                    callback_function=self.handle_coordinate_selection
                )

                # Send the dropdown menu with cancel button
                message = await interaction.response.send_message(
                    "Please select a coordinate to delete:",
                    view=select_view
                )

                # Store the message reference inside the view
                select_view.message = message

        except Exception as e:
            response_embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=response_embed, ephemeral=True)

    async def handle_coordinate_selection(self, interaction: discord.Interaction, selected_coordinate):
        """Handles the selected coordinate for deletion."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.API_URL}/coordinates/{selected_coordinate['guild_id']}/{selected_coordinate['coordinateName']}"
                )

            if response.status_code == 200:
                response_embed = discord.Embed(
                    title="✅ Coordinate Deleted",
                    description=f"Coordinate `{selected_coordinate['coordinateName']}` at (`{selected_coordinate['coordinates']['x']}`, `{selected_coordinate['coordinates']['y']}`, `{selected_coordinate['coordinates']['z']}`) has been successfully deleted!",
                    color=discord.Color.green()
                )
            else:
                error_message = response.json().get("detail", "Unknown error")
                response_embed = discord.Embed(
                    title="⚠️ Error Deleting Coordinate",
                    description=f"Error: {error_message}",
                    color=discord.Color.red()
                )

        except Exception as e:
            response_embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )

        await interaction.response.send_message(embed=response_embed, ephemeral=False)
