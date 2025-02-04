import discord
from discord.ui import Modal, TextInput
import httpx

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
            placeholder="Enter the Dimension", 
            style=discord.TextStyle.short, 
            required=True
        )

        self.add_item(self.name)
        self.add_item(self.x)
        self.add_item(self.y)
        self.add_item(self.z)
        self.add_item(self.dimension)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name.value.strip()
        x = self.x.value.strip()
        y = self.y.value.strip()
        z = self.z.value.strip()
        dimension = self.dimension.value.strip().lower()

        # Validate numeric inputs
        try:
            x = int(x)
            y = int(y)
            z = int(z)
        except ValueError:
            await interaction.response.send_message(
                "Please enter valid integer values for X, Y, and Z.", ephemeral=True
            )
            return
        
        # Construct payload
        data = {
            "guild_id": str(interaction.guild.id),
            "guild_name": interaction.guild.name,
            "channel_id": str(interaction.channel.id),
            "user_id": str(interaction.user.id),
            "username": interaction.user.name,
            "avatar_url": str(interaction.user.avatar.url) if interaction.user.avatar else None,
            "coordinateName": name,
            "coordinates": {"x": x, "y": y, "z": z},
            "dimension": dimension,
        }

        # Send to FastAPI backend
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"http://localhost:8000/coordinates/{interaction.guild.id}/{name}",
                    json=data
                )

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
                await interaction.response.send_message(embed=response_embed, ephemeral=True)
            else:
                raise Exception(f"Server responded with status {response.status_code}: {response.text}")

        except Exception as e:
            await interaction.response.send_message(
                f"⚠️ Error: {str(e)}. Please try again later.", ephemeral=True
            )
