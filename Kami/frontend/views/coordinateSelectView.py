import discord
from discord.ui import Select

class CoordinateSelect(Select):
    def __init__(self, coordinates, callback_function):
        """
        Creates a dropdown menu for coordinate selection.

        :param coordinates: List of MinecraftCoordinate dictionaries.
        :param callback_function: Function to call when a selection is made.
        """
        options = [
            discord.SelectOption(
                label=f"{coord['coordinateName']} ({coord['coordinates']['x']}, {coord['coordinates']['y']}, {coord['coordinates']['z']})",
                value=coord["_id"]  # Use `_id` for unique identification
            )
            for coord in coordinates
        ]
        super().__init__(placeholder="Select a coordinate to overwrite", options=options)
        self.coordinates = coordinates
        self.callback_function = callback_function  # Function to execute on selection

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]  # Get selected `_id`
        selected_coordinate = next(coord for coord in self.coordinates if coord["_id"] == selected_id)
        await self.callback_function(interaction, selected_coordinate)
