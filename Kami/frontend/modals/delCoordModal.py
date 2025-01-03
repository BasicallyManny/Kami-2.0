import discord
from discord.ui import Modal, TextInput

class DelCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Delete Coordinate")

        self.name = TextInput(
            label="Name", 
            placeholder="Enter the name of the coordinate you want to remove", 
            style=discord.TextStyle.short, 
            required=True
        )
        
        self.add_item(self.name)
        
    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        #ADD CHECKS TO CONFIRM THE VALUE IS IN THE DATABASE
        response_embed = discord.Embed(
            title="Coordinate Added",
            description=f"Coordinate `{name}` Removed successfully.",
            color=discord.Color.green()
        )
        
        response_embed.set_author(
            name=interaction.user.display_name, 
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )


        await interaction.response.send_message(embed=response_embed, ephemeral=True)

        
        