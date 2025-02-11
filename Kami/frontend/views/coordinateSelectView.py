import discord
from discord.ui import View, Select, Button
from typing import List, Dict, Any

class CoordinateSelect(Select):
    def __init__(self, coordinates: List[Dict[str, Any]], callback_function=None):
        """Creates a dropdown menu for coordinate selection."""
        options = [
            discord.SelectOption(
                label=f"{coord['coordinateName']}",
                description=f"Coordinates: ({coord['coordinates']['x']}, {coord['coordinates']['y']}, {coord['coordinates']['z']})",
                emoji="📍",
                value=f"{coord['guild_id']}_{coord['coordinateName']}_{str(coord['_id'])}"
            )
            for coord in coordinates
        ]
        
        super().__init__(placeholder="Select a Coordinate", options=options)
        self.coordinates = coordinates
        self.callback_function = callback_function

    async def callback(self, interaction: discord.Interaction):
        """Handles selection from the dropdown."""
        selected_value = self.values[0]
        guild_id, coordinate_name, coord_id = selected_value.split('_')

        selected_coordinate = next(coord for coord in self.coordinates
                               if str(coord['_id']) == coord_id 
                               and coord['guild_id'] == guild_id 
                               and coord['coordinateName'] == coordinate_name)

        # Get the parent view
        view: CoordinateSelectView = self.view

        # Disable the cancel button
        for item in view.children:
            if isinstance(item, CancelButton):
                item.disabled = True

        await interaction.message.edit(view=view)

        if self.callback_function:
            await self.callback_function(interaction, selected_coordinate)

class CancelButton(Button):
    def __init__(self):
        """Creates a cancel button with red color."""
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="Cancel",
            emoji="❌"
        )

    async def callback(self, interaction: discord.Interaction):
        """Handles the cancel button click."""
        await interaction.response.send_message("Selection cancelled.", ephemeral=True)
        self.view.stop()
        await interaction.message.delete()

class CoordinateSelectView(View):
    def __init__(self, coordinates: List[Dict[str, Any]], callback_function=None):
        """Creates a view with both coordinate select dropdown and cancel button."""
        super().__init__()  # Initialize parent View without explicit timeout
        
        # Add the coordinate select dropdown
        self.select = CoordinateSelect(coordinates, callback_function)
        self.add_item(self.select)
        
        # Add the cancel button
        self.cancel_button = CancelButton()
        self.add_item(self.cancel_button)

    async def on_timeout(self):
        """Handles what happens when the view times out."""
        try:
            for item in self.children:
                item.disabled = True
            if hasattr(self, 'message'):
                await self.message.edit(view=self)
        except:
            pass
