import discord
import httpx

class RenameCoordinateModal(discord.ui.Modal, title="Rename Coordinate"):
    new_name = discord.ui.TextInput(
        label="New Coordinate Name",
        placeholder="Enter the new name for the coordinate",
        required=True
    )

    def __init__(self, coord_data):
        super().__init__()
        self.coord_data = coord_data

    async def on_submit(self, interaction: discord.Interaction):
        """Handles user submission of the modal."""
        new_name = self.new_name.value
        api_url = f"http://localhost:8000/coordinates/{self.coord_data['guild_id']}/{self.coord_data['coordinateName']}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(api_url, json={"new_coordinate_name": new_name})

            if response.status_code == 200:
                await interaction.response.send_message(f"✅ Coordinate renamed to `{new_name}`!", ephemeral=True)
            else:
                error_message = response.json().get("detail", "Unknown error")
                await interaction.response.send_message(f"❌ Error: {error_message}", ephemeral=True)

        except httpx.RequestError as e:
            await interaction.response.send_message(f"❌ Request error: {str(e)}", ephemeral=True)