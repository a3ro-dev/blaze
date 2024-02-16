import discord
from discord.ext import commands
import sqlite3
import asyncio

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green) #type: ignore
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()
        await interaction.response.send_message('<a:Loadingblaze:1207643297791873055> Setting up...')
        await asyncio.sleep(3)
        await interaction.response.edit_message(content='<a:success:1207643908016971840> Setup complete.')

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red) #type: ignore
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()
        await interaction.response.send_message('<a:Loadingblaze:1207643297791873055> Stopping setup...')
        await asyncio.sleep(3)
        await interaction.response.edit_message(content='<a:success:1207643908016971840> Setup stopped.')

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setup_ticket(self, ctx, channel: discord.TextChannel, body: str, greeting_embed: str, *role: discord.Role, category: discord.CategoryChannel):
        # Connect to the database
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()

        # Create a table for the guild if it doesn't exist
        guild_id = str(ctx.guild.id)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_id} (channel_id INTEGER, ticketcategory_id INTEGER, body TEXT, greeting_embed TEXT, role_ids TEXT)")

        # Insert the ticket information into the table
        channel_id = channel.id
        ticketcategory_id = category.id
        role_ids = ','.join(str(r.id) for r in role)
        cursor.execute(f"INSERT INTO {guild_id} (channel_id, ticketcategory_id, body, greeting_embed, role_ids) VALUES (?, ?, ?, ?, ?)",
                       (channel_id, ticketcategory_id, body, greeting_embed, role_ids))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        # Create the view
        view = ConfirmView()

        # Send a message with the view
        # Fetch the data from the database
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {guild_id}")
        data = cursor.fetchone()
        conn.close()

        # Create an embed with the fetched data
        embed = discord.Embed(title="Ticket System Setup", color=discord.Color.green())
        embed.add_field(name="Channel", value=f"<#{data[0]}>")
        embed.add_field(name="Category", value=f"<#{data[1]}>")
        embed.add_field(name="Body", value=data[2])
        embed.add_field(name="Greeting Embed", value=data[3])
        embed.add_field(name="Roles", value=', '.join(f"<@&{r}>" for r in data[4].split(',')))

        # Send a message with the embed and the view
        await ctx.send("Please confirm the setup", embed=embed, view=view)

        # Wait for the view to stop
        await view.wait()

        # Check the value of the view
        if view.value is True:
            await ctx.send("Setup confirmed!")
        elif view.value is False:
            await ctx.send("Setup cancelled.")
        
    @commands.command()
    async def ticket(self, ctx):
        await ctx.send("Ticket system is under development")

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))