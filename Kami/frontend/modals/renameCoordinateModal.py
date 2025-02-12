import discord
from discord.ui import Modal, TextInput
import httpx
from views.coordinateSelectView import CoordinateSelectView

class RenameCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Rename Coordinate")

        self.name = TextInput(
            label="Current Coordinate Name", 
            placeholder="Enter the current name of the coordinate", 
            style=discord.TextStyle.short, 
            required=True
        )

        self.new_name = TextInput(
            label="New Coordinate Name",
            placeholder="Enter the new name for the coordinate",
            style=discord.TextStyle.short,
            required=True
        )

        self.add_item(self.name)
        self.add_item(self.new_name)

    async def on_submit(self, interaction: discord.Interaction):
        current_name = self.name.value
        new_name = self.new_name.value
        guild_id = interaction.guild.id  # Server ID for scope

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"http://localhost:8000/coordinates/{guild_id}/{current_name}")
                coordinates = response.json()

                if not coordinates:
                    response_embed = discord.Embed(
                        title="❌ Coordinate Not Found",
                        description=f"Could not find a coordinate named `{current_name}`.",
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=response_embed, ephemeral=True)
                    return

                if len(coordinates) == 1:
                    # Rename directly if only one coordinate is found
                    async with httpx.AsyncClient() as client:
                        rename_response = await client.patch(
                            f"http://localhost:8000/coordinates/{guild_id}/{current_name}?new_name={new_name}"
                        )

                    if rename_response.status_code == 200:
                        response_embed = discord.Embed(
                            title="✅ Coordinate Renamed",
                            description=f"Coordinate `{current_name}` has been renamed to `{new_name}` successfully!",
                            color=discord.Color.green()
                        )
                    else:
                        error_message = rename_response.json().get("detail", "Unknown error")
                        response_embed = discord.Embed(
                            title="⚠️ Error Renaming Coordinate",
                            description=f"Error: {error_message}",
                            color=discord.Color.red()
                        )

                    await interaction.response.send_message(embed=response_embed, ephemeral=False)
                    return

                # Ensure valid data format
                if not isinstance(coordinates, list) or not all(isinstance(coord, dict) for coord in coordinates):
                    await interaction.response.send_message("⚠️ Error: Coordinate data format is incorrect.", ephemeral=True)
                    return

                # Show dropdown menu for selection
                select_view = CoordinateSelectView(
                    coordinates=coordinates,
                    callback_function=self.handle_coordinate_selection
                )

                message = await interaction.response.send_message(
                    "Multiple coordinates found. Please select one to rename:",
                    view=select_view
                )

                select_view.message = message  # Store reference

        except Exception as e:
            response_embed = discord.Embed(
                title="⚠️ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=response_embed, ephemeral=True)

    async def handle_coordinate_selection(self, interaction: discord.Interaction, selected_coordinate):
        """Handles the renaming process after a coordinate is selected."""
        new_name = self.new_name.value  # Get the new name from the modal input
        guild_id = interaction.guild.id  # Get the guild ID from the interaction

        # Extract the coordinateName from the selected coordinate
        current_name = selected_coordinate['coordinateName']

        try:
            async with httpx.AsyncClient() as client:
                # Send the PATCH request with new_name as a query parameter
                rename_response = await client.patch(
                    f"http://localhost:8000/coordinates/{guild_id}/{current_name}?new_name={new_name}"
                )

            if rename_response.status_code == 200:
                response_embed = discord.Embed(
                    title="✅ Coordinate Renamed",
                    description=f"Coordinate `{current_name}` has been successfully renamed to `{new_name}`.",
                    color=discord.Color.green()
                )   
            else:
                error_message = rename_response.json().get("detail", "Unknown error")
                response_embed = discord.Embed(
                    title="⚠️ Error Renaming Coordinate",
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


