import datetime
import sqlite3
import time

import discord
from discord.ext import commands
import config as cfg

class Ticket(commands.Cog):
    """This is responsible for the ticket system"""

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command()
    async def setup_ticket(self, ctx, category_id: int, panelMessage: str, roles: commands.Greedy[discord.Role]):
        guild_id = 'guild' + str(ctx.guild.id)
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {guild_id} (category_id INTEGER, panel_MSG TEXT, role_ids TEXT)")
        role_ids = ','.join(str(role.id) for role in roles)
        cursor.execute(
            f"INSERT INTO {guild_id} (category_id, panel_MSG, role_ids) VALUES (?, ?, ?)",
            (category_id, panelMessage, role_ids))
        conn.commit()
        conn.close()

    @discord.ui.button(label='Ticket', style=discord.ButtonStyle.green, custom_id='Ticket:green')
    async def ticketopen(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild_id = 'guild' + str(interaction.guild.id)
        conn = sqlite3.connect('db/tickets.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT category_id, panel_MSG, role_ids FROM {guild_id}")
        row = cursor.fetchone()
        conn.close()

        if row is not None:
            category_id, panel_MSG, role_ids = row
            category = discord.utils.get(interaction.guild.categories, id=int(category_id))
            roles = [discord.utils.get(interaction.guild.roles, id=int(role_id)) for role_id in role_ids.split(',')]
            panelMessage = panel_MSG

            if row is not None:
                panelMessage = row[0]

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(
                    read_messages=False,
                    view_channel=False
                ),
                interaction.user: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                )}
            for role in roles:
                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True,
                    manage_permissions=True
                )
            await ticket.edit(overwrites=overwrites)
            await interaction.response.send_message(f'Your Ticket has been opened. Please move to {ticket.mention}',
                                                    ephemeral=True)
            user = interaction.user.name
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            serverNAME = interaction.guild.name
            embed = discord.Embed(title=f'This ticket is opened by {interaction.user.mention}.',
                                  description=,
                                  color=cfg.CLR)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'{interaction.guild.name} | {interaction.guild.id}', icon_url=interaction.guild.icon.url)
            view = CLOSE()
            msg = await ticket.send(content=f'{interaction.user.mention} | {panel_MSG}', embed=embed, view=view)
            await msg.pin()


class CLOSE(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='CLOSE', style=discord.ButtonStyle.danger, custom_id='CLOSE:RED')
    async def closeticket(self, interaction=discord.Interaction, button=discord.ui.Button, ):
        await interaction.channel.send(f'This ticket was closed by {interaction.user.mention}')
        channel = interaction.channel
        time.sleep(10)
        await channel.delete()