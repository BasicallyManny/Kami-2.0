import discord
import httpx

class ConfirmOverwriteView(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data
        
    #Overwrite the already saved Data
    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.danger)
    async def overwrite(self, interaction: discord.Interaction, button: discord.ui.Button):
        api_url = f"http://localhost:8000/coordinates/{self.data['guild_id']}/{self.data['coordinateName']}"

        # Directly send the original data for overwrite
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(api_url, json=self.data)

            if response.status_code == 200:
                # Proceed to add the coordinate after overwrite
                await self.send_post_request(interaction)
            else:
                error_message = response.json().get("detail", "Unknown error")
                await interaction.response.send_message(f"⚠️ Error: {error_message}", ephemeral=True)

        except httpx.RequestError as e:
            await interaction.response.send_message(f"❌ Request error: {str(e)}", ephemeral=True)
            
    #add the coordinate normally
    @discord.ui.button(label="continue", style=discord.ButtonStyle.success)
    async def add_coordinate(self, interaction: discord.Interaction, button: discord.ui.Button, data):
        try:
            name = data["coordinateName"]
            x = data["coordinates"]["x"]
            y = data["coordinates"]["y"]
            z = data["coordinates"]["z"]
            dimension = data["dimension"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"http://localhost:8000/coordinates/{interaction.guild.id}/{name}", json=data)

            # Handle response
            if response.status_code == 200:
                response_embed = discord.Embed(
                    title="✅ Coordinate Added",
                    description=f"Coordinate `{name}` added successfully!",
                    color=discord.Color.green()
                )
                response_embed.set_author(
                    name=interaction.user.display_name, 
                    icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                )
                response_embed.add_field(
                    name="Coordinates", 
                    value=f"**X:** {x}\n**Y:** {y}\n**Z:** {z}\n**Dimension:** {dimension}",
                    inline=False
                )
                await interaction.followup.send(embed=response_embed)
                
            else:
                raise Exception(f"Server responded with status {response.status_code}: {response.text}")

        except Exception as e:
            await interaction.followup.send(
                f"⚠️ Error: {str(e)}. Please try again later.", ephemeral=True
            )
    #if the user decides to cancel
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Operation canceled.", ephemeral=True)