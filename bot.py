import discord
from discord.ext import commands
from discord import ui

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ticket_category_id = 1332771593331408947  # Replace with your actual category ID
booking_boost_channel_id = 123456789012345678  # Replace with your actual channel ID
feedback_channel_id = 1332771255186882630  # Replace with your actual feedback channel ID

class TicketButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=discord.utils.get(guild.categories, id=ticket_category_id),
            overwrites=overwrites
        )
        
        embed = discord.Embed(title="Ticket Created", description="A staff member will be with you shortly. Use the button below to close the ticket.", color=discord.Color.blue())
        view = TicketCloseButton()
        await ticket_channel.send(f"{interaction.user.mention}, your ticket has been created!", embed=embed, view=view)
        await interaction.response.send_message(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

class FeedbackModal(ui.Modal, title="User Feedback"):
    boost_type = ui.TextInput(label="Boost Type", placeholder="Enter boost type (e.g., Mythic 10)")
    rating = ui.TextInput(label="Rating (1-10)", placeholder="Rate your experience", max_length=2)

    def __init__(self, ticket_channel):
        super().__init__()
        self.ticket_channel = ticket_channel

    async def on_submit(self, interaction: discord.Interaction):
        feedback_channel = interaction.guild.get_channel(feedback_channel_id)
        if feedback_channel:
            embed = discord.Embed(color=discord.Color.green())
            embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            embed.title = "Feedback"
            embed.add_field(name="Boost:", value=self.boost_type.value, inline=False)
            embed.add_field(name="Score:", value=f"{self.rating.value}/10", inline=False)
            embed.set_footer(text="Thank you for your feedback!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await feedback_channel.send(embed=embed)
            await interaction.response.send_message("Thank you for your feedback! Closing the ticket now.", ephemeral=True)

            # Ensure the ticket channel still exists before attempting to delete
            if self.ticket_channel and self.ticket_channel in interaction.guild.channels:
                await self.ticket_channel.delete()
        else:
            await interaction.response.send_message("Error: Feedback channel not found.", ephemeral=True)

class TicketCloseButton(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        modal = FeedbackModal(interaction.channel)
        await interaction.response.send_modal(modal)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(TicketButton())
    bot.add_view(TicketCloseButton())

@bot.command()
async def setup_ticket(ctx):
    embed = discord.Embed(title="Ticket System", description="Click the button below to open a ticket.", color=discord.Color.blue())
    view = TicketButton()
    await ctx.send(embed=embed, view=view)

bot.run("Your-token")
