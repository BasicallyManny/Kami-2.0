import discord
from discord.ui import Modal, TextInput

class AddCoordModal(Modal):
    def __init__(self):
        super().__init__(title="Add Coordinate")

        self.name = TextInput(
            label="Name", 
            placeholder="Enter a name for the coordinate", 
            style=discord.TextStyle.short, 
            required=True
        )
        self.x = TextInput(
            label="X", 
            placeholder="Enter the X coordinate", 
            style=discord.TextStyle.short, 
            required=True, 
            max_length=4
        )
        self.y = TextInput(
            label="Y", 
            placeholder="Enter the Y coordinate", 
            style=discord.TextStyle.short, 
            required=True, 
            max_length=4
        )
        self.z = TextInput(
            label="Z", 
            placeholder="Enter the Z coordinate", 
            style=discord.TextStyle.short, 
            required=True, 
            max_length=4
        )
        self.dimension = TextInput(
            label="Dimension", 
            placeholder="Enter the dimension (e.g., Overworld, Nether, End)", 
            style=discord.TextStyle.short, 
            required=True, 
            max_length=100
        )

        self.add_item(self.name)
        self.add_item(self.x)
        self.add_item(self.y)
        self.add_item(self.z)
        self.add_item(self.dimension)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value
        x = self.x.value
        y = self.y.value
        z = self.z.value
        dimension = self.dimension.value

        try:
            x = int(x)
            y = int(y)
            z = int(z)
        except ValueError:
            await interaction.response.send_message(
                "Please enter valid numeric values for X, Y, and Z.", ephemeral=True
            )
            return

        response_embed = discord.Embed(
            title="Coordinate Added",
            description=f"Coordinate `{name}` added successfully.",
            color=discord.Color.green()
        )
        response_embed.set_author(
            name=interaction.user.display_name, 
            icon_url=interaction.user.avatar.url if interaction.user.avatar else None
        )
        response_embed.add_field(
            name="Coordinates", 
            value=f"X: {x}\nY: {y}\nZ: {z}\nDimension: {dimension}", 
            inline=False
        )

