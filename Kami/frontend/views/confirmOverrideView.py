from bson import ObjectId
import discord
import httpx
from views.coordinateSelectView import CoordinateSelect

class ConfirmOverwriteView(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data

    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.primary)
    async def overwrite(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Debugging: Log when the button is clicked
        print("Overwrite button clicked!")

        await interaction.response.defer()  # Defer the response to avoid timeouts
        api_url = f"http://localhost:8000/coordinates-with-id/{self.data['guild_id']}/{self.data['coordinateName']}"

        try:
            # Debugging: Log the API URL and data being sent
            print(f"API URL: {api_url}")
            print(f"Data: {self.data}")

            #TODO: Fetch existing coordinates 
            
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url)

            # Debugging: Check the API response
            print(f"API Response Status: {response.status_code}")
            print(f"API Response Body: {response.text}")

            if response.status_code == 200:
                coordinates = response.json()

                # If multiple coordinates with the same name, let the user select
                if len(coordinates) > 1:
                    await self.prompt_user_selection(interaction, coordinates)
                elif len(coordinates) == 1:
                    await self.overwrite_coordinate(interaction, coordinates[0])
                else:
                    await interaction.followup.send("❌ No coordinates found with the provided name.")
                    return

            else:
                await interaction.followup.send(f"⚠️ Error: {response.status_code} - {response.text}")
                return

        except httpx.RequestError as e:
            print(f"Request Error: {str(e)}")  # Debugging: Log request errors
            await interaction.followup.send(f"❌ Request error: {str(e)}")

    async def overwrite_coordinate(self, interaction: discord.Interaction, coordinate):
        """Overwrites the chosen coordinate"""
        print("Overwriting coordinate...")  # Debugging: Log when overwriting happens
        api_url = f"http://localhost:8000/coordinates-with-id/{self.data['guild_id']}/{coordinate['_id']}"

        async with httpx.AsyncClient() as client:
            response = await client.put(api_url, json=self.data)

        if response.status_code == 200:
            embed = discord.Embed(
                title="✅ Coordinate Overwritten",
                description=f"Coordinate `{coordinate['coordinateName']}` has been successfully overwritten!",
                color=discord.Color.green()
            )
        else:
            error_message = response.json().get("detail", "Unknown error")
            embed = discord.Embed(
                title="⚠️ Error Overwriting Coordinate",
                description=f"Error: {error_message}",
                color=discord.Color.red()
            )

        await interaction.followup.send(embed=embed)



    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Operation canceled.", ephemeral=True)

        # Disable all buttons after cancel is pressed
        for item in self.children:  # Iterating over all buttons
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        # Update the message to reflect the disabled buttons
        await interaction.message.edit(view=self)
