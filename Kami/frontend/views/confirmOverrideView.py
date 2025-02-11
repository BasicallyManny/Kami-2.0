import discord
import httpx
from views.coordinateSelectView import CoordinateSelectView 

class ConfirmOverwriteView(discord.ui.View):
    def __init__(self, data, coordinate_list):
        super().__init__()
        self.data = data
        self.coordinate_list=coordinate_list
        
    @discord.ui.button(label="Add Anyway", style=discord.ButtonStyle.green)
    async def add_anyway(self, interaction: discord.Interaction, button: discord.ui.Button):

        api_url = f"http://localhost:8000/coordinates/{self.data['guild_id']}/{self.data['coordinateName']}"

        await interaction.response.defer()  # Deferring the response to avoid timeouts

        try:
            # Send the POST request to add the coordinate
            async with httpx.AsyncClient() as client:
                response = await client.post(api_url, json=self.data)

            if response.status_code == 200:
                # Successfully added, so confirm with an embed
                response_embed = discord.Embed(
                    title="✅ Coordinate Added",
                    description=f"Coordinate `{self.data['coordinateName']}` has been successfully added!",
                    color=discord.Color.green()
                )
                response_embed.set_author(
                    name=interaction.user.display_name,
                    icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                )
                await interaction.followup.send(embed=response_embed)
            else:
                error_message = response.json().get("detail", "Unknown error")
                response_embed = discord.Embed(
                    title="⚠️ Error Adding Coordinate",
                    description=f"Error: {error_message}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=response_embed)

            # Disable all buttons after any button is pressed
            for item in self.children:  # Iterating over all buttons
                if isinstance(item, discord.ui.Button):
                    item.disabled = True

            # Update the message to reflect the disabled buttons
            await interaction.message.edit(view=self)

        except httpx.RequestError as e:
            await interaction.followup.send(f"❌ Request error: {str(e)}")
     
             
    # Overwrite or add the coordinate

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.primary)
    async def overwrite(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handles the overwrite button click."""
        await interaction.response.defer()  # Defer response to avoid timeout

        try:
            # Ensure self.data is a list and contains valid coordinate dictionaries
            if not isinstance(self.coordinate_list, list) or not all(isinstance(coord, dict) for coord in self.coordinate_list):
                await interaction.followup.send("⚠️ Error: Coordinate data is not in the correct format.", ephemeral=True)
                return

            # Create CoordinateSelectView with the coordinate data
            select_view = CoordinateSelectView(
                coordinates=self.coordinate_list,
                callback_function=self.handle_coordinate_selection
            )

            # Disable all buttons after pressing
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.disabled = True

            # Update the message to reflect the disabled buttons
            await interaction.message.edit(view=self)

            # Send the dropdown menu with cancel button and store the message
            message = await interaction.followup.send(
                "Please select a coordinate to overwrite:",
                view=select_view
            )
            select_view.message = message  # Store message reference for cleanup

        except discord.errors.InteractionResponded:
            await interaction.followup.send(
                "⚠️ Error: This interaction has already been responded to.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Unexpected error: {str(e)}",
                ephemeral=True
            )

    # Cancel the operation and disable all buttons
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Operation canceled.", ephemeral=True)

        # Disable all buttons after cancel is pressed
        for item in self.children:  # Iterating over all buttons
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        # Update the message to reflect the disabled buttons
        await interaction.message.edit(view=self)
        
     #OVERWRITE THE SELECTED COORDINATE IF OVERWRITE IS PRESSED
    async def handle_coordinate_selection(self, interaction: discord.Interaction, selected_coordinate):
        """
        Callback function to handle coordinate selection.
        This will be called when a coordinate is selected from the dropdown.
        """
        try:
            # Handle the selected coordinate here
            # You can add your logic for what should happen when a coordinate is selected
            await interaction.response.send_message(
                f"Processing overwrite for coordinate: {selected_coordinate['coordinateName']}",
                ephemeral=True
            )
            print(f"selectedCoordinate: {selected_coordinate}")
            print(f"self.data: {self.data}")
            
            # Add your overwrite logic here
            api_url = f"http://localhost:8000/coordinates/{selected_coordinate['guild_id']}/{selected_coordinate['coordinateName']}"
            #Call fastAPI endpoint to overwrite Coordinate
            async with httpx.AsyncClient() as client:
                response = await client.put(api_url, json=self.data)
            
            if response.status_code == 200:
                # Successfully added, so confirm with an embed
                response_embed = discord.Embed(
                    title="✅ Coordinate Overwritten",
                    description=f"Coordinate `{selected_coordinate['coordinateName']}` at (`{selected_coordinate['coordinates']['x']}`, `{selected_coordinate['coordinates']['y']}`, `{selected_coordinate['coordinates']['z']}`) has been successfully overwritten!",

                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=response_embed, ephemeral=False)
            else:
                #Display Success or Failure Message
                error_message = response.json().get("detail", "Unknown error")
                response_embed = discord.Embed(
                    title="⚠️ Error Overwriting Coordinate",
                    description=f"Error: {error_message}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=response_embed, ephemeral=False)
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error processing selection: {str(e)}",
                ephemeral=True
            )