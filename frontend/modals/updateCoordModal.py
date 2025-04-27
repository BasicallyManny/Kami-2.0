import os
from dotenv import load_dotenv

import discord
from discord.ui import Modal, TextInput
import httpx
from views.coordinateSelectView import CoordinateSelectView

class UpdateCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Delete Coordinate")
        
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
        """Handles the submission of the modal."""
        return

    async def handle_coordinate_selection(self, interaction: discord.Interaction, selected_coordinate):
        """Handles the selected coordinate for update."""
        return
