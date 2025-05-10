import json
import os
from dotenv import load_dotenv

import discord
from discord.ui import Modal, TextInput, View, Button
import httpx
from views.coordinateSelectView import CoordinateSelectView
from modals.updateModal import UpdateModal

class UpdateCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Update Coordinate")
        
        load_dotenv()
        self.API_URL = os.getenv('API_URL')
        
        self.name = TextInput(
            label="Coordinate Name", 
            placeholder="Enter the name of the coordinate to update", 
            style=discord.TextStyle.short, 
            required=True
        )
        self.add_item(self.name)
        
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        guild_id = interaction.guild.id
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.API_URL}/coordinates/{guild_id}/{name}")
                coordinates = response.json()

                # Handle not found
                if isinstance(coordinates, dict) and coordinates.get("detail") == '404: Coordinate Name not found':
                    embed = discord.Embed(
                        title="❌ Coordinate Not Found",
                        description=f"Could not find a coordinate named `{name}`.",
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return

                # Validate list structure
                if not isinstance(coordinates, list) or not all(isinstance(c, dict) for c in coordinates):
                    await interaction.response.send_message("⚠️ Error: Invalid coordinate format from API.", ephemeral=True)
                    return
                
                # More than one coordinate found — show select dropdown
                select_view = CoordinateSelectView(
                    coordinates=coordinates,
                    callback_function=self.handle_coordinate_selection
                )

                message = await interaction.response.send_message(
                    "Please select a coordinate to update:",
                    view=select_view
                )
                select_view.message = message

        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    async def handle_coordinate_selection(self, interaction: discord.Interaction, selected_coordinate):
        try:
            print("Selected coordinate for update:")
            print(json.dumps(selected_coordinate, indent=4))

            update_modal = UpdateModal(selected_coordinate)
            await interaction.response.send_modal(update_modal)

        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
