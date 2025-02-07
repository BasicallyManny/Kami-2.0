import discord
import httpx

class ConfirmOverwriteView(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data
        
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
        api_url = f"http://localhost:8000/coordinates/{self.data['guild_id']}/{self.data['coordinateName']}"

        await interaction.response.defer()  # Deferring the response to avoid timeouts

        try:
            # Send the PUT request to overwrite the coordinate
            async with httpx.AsyncClient() as client:
                response = await client.put(api_url, json=self.data)

            if response.status_code == 200:
                # Successfully overwrote, so confirm with an embed
                response_embed = discord.Embed(
                    title="✅ Coordinate Overwritten",
                    description=f"Coordinate `{self.data['coordinateName']}` has been successfully overwritten!",
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
                    title="⚠️ Error Overwriting Coordinate",
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
            await interaction.followup.send(
                content=f"❌ Request error: {str(e)}",
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
        
