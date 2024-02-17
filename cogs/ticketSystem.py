import discord
from discord.ext import commands
import sqlite3
import asyncio

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green) #type: ignore
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction[discord.Client]):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red) #type: ignore
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction[discord.Client]):
        self.value = False
        self.stop()

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Open Ticket', style=discord.ButtonStyle.green) #type: ignore
    async def open_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild_id = 'guild' + str(interaction.guild.id) #type: ignore
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {guild_id}")
        row = cursor.fetchone()
        conn.close()

        if row is not None:
            category_id = row[1]
            category = interaction.guild.get_channel(category_id) #type: ignore
            ticket_channel = await category.create_text_channel('ticket', topic=f"Ticket for {interaction.user.mention}") #type: ignore
            ticket_channel.send(f"{interaction.user.mention}'s ticket", view=ConfirmView()).__await__()

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def setup_ticket(self, ctx, channel: discord.TextChannel, body: str, greeting_embed: str, roles: commands.Greedy[discord.Role], category: discord.CategoryChannel):
        # Connect to the database
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()

        # Create a table for the guild if it doesn't exist
        guild_id = 'guild' + str(ctx.guild.id)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_id} (channel_id INTEGER, ticketcategory_id INTEGER, body TEXT, greeting_embed TEXT, role_ids TEXT)")

        # Insert the ticket information into the table
        channel_id = channel.id
        ticketcategory_id = category.id
        role_ids = ','.join(str(r.id) for r in roles)
        cursor.execute(f"INSERT INTO {guild_id} (channel_id, ticketcategory_id, body, greeting_embed, role_ids) VALUES (?, ?, ?, ?, ?)",
                       (channel_id, ticketcategory_id, body, greeting_embed, role_ids))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Create the view
        view = TicketView()

        # Send a message with the view
        await channel.send(body, view=view)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))