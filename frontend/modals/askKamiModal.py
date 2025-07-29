import discord
from discord.ui import Modal, TextInput, View, Button
import httpx
import asyncio
from backend.models.chatbotModels import ChatRequest, ChatResponse
import os


class AskKamiModal(Modal):
    
    def __init__(self):
        super().__init__(title="Ask Kami - Minecraft AI Assistant")
        
        self.question = TextInput(
            label="Hi there! What would you like to ask Kami?", 
            placeholder="Ask a Minecraft-related question (e.g., How do I build a netherite farm?)", 
            style=discord.TextStyle.paragraph, 
            required=True,
            max_length=2000
        )
        
        self.add_item(self.question)

    async def on_submit(self, interaction: discord.Interaction):
        question = self.question.value.strip()
        
        if not question:
            await interaction.response.send_message("Please enter a question.", ephemeral=True)
            return
        
        # Send initial loading response
        loading_embed = discord.Embed(
            title="🔍 Searching for information...",
            description="Kami is working on your question. This may take a moment.",
            color=0x00ff00
        )
        loading_embed.set_footer(text="Powered by Kami AI • Minecraft Expert Assistant")
        
        await interaction.response.send_message(embed=loading_embed)
        
        # Start loading animation
        loading_states = [
            ("🔍 Searching for information...", "Kami is working on your question. This may take a moment."),
            ("🤖 Kami is thinking...", "Analyzing your Minecraft question..."),
            ("📚 Gathering resources...", "Looking up the best tutorials and guides..."),
            ("⚡ Processing your question...", "Compiling the most helpful information..."),
            ("🔨 Crafting the perfect answer...", "Almost ready with your response...")
        ]
        
        # Get the original response message
        original_message = await interaction.original_response()
        
        # Start loading animation task
        loading_task = asyncio.create_task(self._animate_loading(original_message, loading_states))
        API_URL = os.getenv("API_URL", "http://localhost:8000")  # Default to local API if not set
        
        try:
            # Call the API to get response from Kami
            async with httpx.AsyncClient(timeout=60.0) as client:
                api_url = f"{API_URL}/chatbot/{interaction.guild_id}/{interaction.channel_id}" 
                # Prepare request data
                #build session_id from guild and channel IDs
                session_id = f"{interaction.guild_id}-{interaction.channel_id}-{interaction.user.id}"
                
                request_data:ChatRequest = {
                    "query": question,
                    "session_id": session_id
                }
                
                response:ChatResponse = await client.post(api_url, json=request_data)
                
            # Cancel loading animation
            loading_task.cancel()
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data: {data}")  # Debugging line
                answer = data.get("answer", "I couldn't find an answer to your question.")
                urls = data.get("urls", [])
                # Create response embed
                embed = discord.Embed(
                    title="🤖 Kami's Response",
                    description=answer,
                    color=0x00ff00
                )
                
                # Add user info
                embed.set_author(
                    name=f"Asked by {interaction.user.display_name}",
                    icon_url=interaction.user.avatar.url if interaction.user.avatar else None
                )
                
                # Add question as field
                embed.add_field(
                    name="📝 Your Question",
                    value=question,
                    inline=False
                )
                
                # Add URLs if available
                if urls:
                    url_text = "\n".join([f"• [Resource {i+1}]({url})" for i, url in enumerate(urls[:5])])
                    embed.add_field(
                        name="🔗 Helpful Resources",
                        value=url_text,
                        inline=False
                    )
                
                embed.set_footer(text="Powered by Kami AI • Minecraft Expert Assistant")
                
                # Create view with additional options
                view = KamiResponseView(question, interaction.user.id, interaction.guild_id, interaction.channel_id)
                
                await original_message.edit(embed=embed, view=view)
                
            else:
                error_embed = discord.Embed(
                    title="❌ Error",
                    description=f"API returned status code: {response.status_code}",
                    color=0xff0000
                )
                error_embed.set_footer(text="Please try again later.")
                await original_message.edit(embed=error_embed)
                
        except httpx.TimeoutException:
            # Cancel loading animation
            loading_task.cancel()
            
            timeout_embed = discord.Embed(
                title="⏰ Request Timeout",
                description="The request took too long to process. Please try again.",
                color=0xff9900
            )
            await original_message.edit(embed=timeout_embed)
            
        except Exception as e:
            # Cancel loading animation
            loading_task.cancel()
            
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            error_embed.set_footer(text="Please try again later.")
            await original_message.edit(embed=error_embed)

    async def _animate_loading(self, message, states):
        """Animate the loading message"""
        try:
            index = 0
            while True:
                title, description = states[index]
                embed = discord.Embed(
                    title=title,
                    description=description,
                    color=0x00ff00
                )
                embed.set_footer(text="Powered by Kami AI • Minecraft Expert Assistant")
                await message.edit(embed=embed)
                index = (index + 1) % len(states)
                await asyncio.sleep(2)  # Change state every 2 seconds
        except asyncio.CancelledError:
            pass  # Task was cancelled, which is expected

class KamiResponseView(View):
    def __init__(self, original_question, user_id, guild_id, channel_id):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.original_question = original_question
        self.user_id = user_id
        self.guild_id = guild_id
        self.channel_id = channel_id

    @discord.ui.button(label="Ask New Question", style=discord.ButtonStyle.secondary, emoji="🔄")
    async def ask_new(self, interaction: discord.Interaction, button: Button):
        """Allow user to ask a completely new question"""
        modal = AskKamiModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Help", style=discord.ButtonStyle.secondary, emoji="❓")
    async def help_button(self, interaction: discord.Interaction, button: Button):
        """Show help information"""
        help_embed = discord.Embed(
            title="🤖 Kami - Minecraft AI Assistant",
            description="Ask me anything about Minecraft!",
            color=0x00ff00
        )
        
        help_embed.add_field(
            name="💡 Example Questions",
            value="• How do I build a netherite farm?\n• What's the best way to find diamonds?\n• How do I make an automatic farm?\n• What are the new features in 1.21?",
            inline=False
        )
        
        help_embed.add_field(
            name="🔍 What I can help with",
            value="• Building tutorials and guides\n• Game mechanics and strategies\n• Latest Minecraft updates\n• Farming and automation\n• Redstone contraptions",
            inline=False
        )
        
        help_embed.set_footer(text="Powered by Kami AI • Minecraft Expert Assistant")
        
        await interaction.response.send_message(embed=help_embed, ephemeral=True)


