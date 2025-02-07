import discord
import httpx
from modals.renameCoordinateModal import RenameCoordinateModal

class ConfirmOverwriteView(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.data = data

    #if the user decides to add the coordinate the way it its.
    @discord.ui.button(label="Continue", style=discord.ButtonStyle.danger)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        #NEED IMPLEMENTATION
        pass
    #if the user decides to override the name of coordinate that already exists
   
    @discord.ui.button(label="Overwrite", style=discord.ButtonStyle.secondary)
    async def overwrite(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Trigger the RenameCoordinateModal
        await interaction.response.send_modal(RenameCoordinateModal(self.data))
    
    #if the user decides to cancel
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Operation canceled.", ephemeral=True)
