import os
import json
import discord
from discord.ui import Modal, TextInput
from dotenv import load_dotenv
import httpx
from backend.models.coordinates import CoordinateUpdatePayload

class UpdateModal(Modal):
    def __init__(self, coordinates: dict):
        super().__init__(title="Update Coordinate")
        load_dotenv()
        self.coordinates = coordinates
        self.API_URL = os.getenv('API_URL')
        
        # Extract values with careful fallbacks
        coordinate_name = ""
        if coordinates and 'coordinateName' in coordinates:
            coordinate_name = str(coordinates['coordinateName'])
        
        x_value = ""
        y_value = ""
        z_value = ""
        if coordinates and 'coordinates' in coordinates:
            if 'x' in coordinates['coordinates']:
                x_value = str(coordinates['coordinates']['x'])
            if 'y' in coordinates['coordinates']:
                y_value = str(coordinates['coordinates']['y'])
            if 'z' in coordinates['coordinates']:
                z_value = str(coordinates['coordinates']['z'])
        
        dimension_value = ""
        if coordinates and 'dimension' in coordinates:
            dimension_value = str(coordinates['dimension'])

        # Create TextInputs with explicit unpacking of values
        self.name = TextInput(
            label="Coordinate Name",
            default=coordinate_name,
            style=discord.TextStyle.short,
            required=True
        )

        self.x = TextInput(
            label="X",
            default=x_value,
            style=discord.TextStyle.short,
            required=True
        )

        self.y = TextInput(
            label="Y",
            default=y_value,
            style=discord.TextStyle.short,
            required=True
        )

        self.z = TextInput(
            label="Z",
            default=z_value,
            style=discord.TextStyle.short,
            required=True
        )

        self.dimension = TextInput(
            label="Dimension",
            default=dimension_value,
            style=discord.TextStyle.short,
            required=True
        )

        self.add_item(self.name)
        self.add_item(self.x)
        self.add_item(self.y)
        self.add_item(self.z)
        self.add_item(self.dimension)

    async def on_submit(self, interaction: discord.Interaction):
        # First, acknowledge the interaction to prevent timeout
        await interaction.response.defer(ephemeral=True)
        
        name = self.name.value.strip()
        x = int(self.x.value.strip())
        y = int(self.y.value.strip())
        z = int(self.z.value.strip())
        dimension = self.dimension.value.strip().lower()

        guild_id = str(interaction.guild.id)  # Ensure guild_id is a string
        coordinate_id = self.coordinates['_id']

        payload = {
            "coordinateName": name,
            "coordinates": {
                "x": x,
                "y": y,
                "z": z
            },
            "dimension": dimension,
        }
        
        try:
            # Since the FastAPI route expects guild_id as a query parameter
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.API_URL}/coordinates/{coordinate_id}",
                    params={"guild_id": guild_id},  # Pass guild_id as a query parameter
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    success_embed = discord.Embed(
                        title="✅ Coordinate Updated",
                        description=f"Coordinate `{name}` has been updated successfully.",
                        color=discord.Color.green()
                    )
                    await interaction.followup.send(embed=success_embed, ephemeral=True)
                else:
                    error_embed = discord.Embed(
                        title="❌ Error Updating Coordinate",
                        description=f"Failed to update coordinate `{name}`. Status code: {response.status_code}. Response: {response.text}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=error_embed, ephemeral=True)
        except httpx.RequestError as e:
            error_embed = discord.Embed(
                title="❌ Request Error",
                description=f"An error occurred while making the request: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        except httpx.HTTPStatusError as e:
            error_embed = discord.Embed(
                title="❌ HTTP Error",
                description=f"Received an error response: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Unexpected Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)