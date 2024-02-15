import sqlite3
import discord
from discord.ext import commands
import config as cfg
from datetime import datetime
import asyncio

class ConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green) #type: ignore
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red) #type: ignore
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()

class ModCog(commands.Cog):
    """
    A Cog that provides moderation commands.
    """
    def __init__(self, bot):
        """
        Construct a new 'ModCog' object.

        :param bot: The instance of the bot that the cog is being loaded into.
        """
        self.bot = bot
        self.conn = sqlite3.connect(cfg.modDB)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS guilds
                     (guild_id integer, log_channel integer, welcome_channel integer, main_admin integer)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS warnings
                     (guild_id integer, user_id integer, reason text)''')
        self.conn.commit()



    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx, log_channel: discord.TextChannel, welcome_channel: discord.TextChannel, main_admin: discord.Member):
        """
        Setup the moderation settings for the guild.
        """
        try:
            embed = discord.Embed(title="Setup Verification", color=cfg.CLR)
            embed.add_field(name="Log Channel", value=log_channel.mention, inline=False)
            embed.add_field(name="Welcome Channel", value=welcome_channel.mention, inline=False)
            embed.add_field(name="Main Admin", value=main_admin.mention, inline=False)
            embed.set_footer(text="Please confirm these settings.", icon_url=cfg.FOOTER)

            view = ConfirmView()
            await ctx.send(embed=embed, view=view)
            await view.wait()

            if view.value is True:
                await ctx.send("Setting up... :loading:")
                await asyncio.sleep(3)

                self.cursor.execute("INSERT INTO guilds VALUES (?, ?, ?, ?)",
                                    (ctx.guild.id, log_channel.id, welcome_channel.id, main_admin.id))
                self.conn.commit()

                await ctx.send("Setup complete. :white_check_mark:")
            else:
                await ctx.send("Stopping setup... :loading:")
                await asyncio.sleep(0.5)
                await ctx.edit("Reverting Changed... :loading:")
                await asyncio.sleep(0.5)                
                await ctx.edit("Clearing data... :loading:")
                await asyncio.sleep(3)
                await ctx.send("Setup stopped. :x:")
        except Exception as e:
            embed = discord.Embed(title=f"Error: {str(e)}", color=cfg.CLR)
            await ctx.send(embed=embed)

    @commands.hybrid_command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        """
        Warn a member.
        """
        try:
            self.cursor.execute("INSERT INTO warnings VALUES (?, ?, ?)",
                                (ctx.guild.id, member.id, reason))
            self.conn.commit()

            embed = discord.Embed(title="Warning Issued", color=cfg.CLR)
            embed.add_field(name="User Warned", value=member.mention, inline=False)
            embed.add_field(name="Warned by", value=ctx.author.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text="Warning Issued at", icon_url=cfg.FOOTER)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

            log_channel = self.get_log_channel(ctx.guild.id)
            if log_channel is not None:
                embed = discord.Embed(title="Warning Logged", color=cfg.CLR)
                embed.add_field(name="User Warned", value=member.mention, inline=False)
                embed.add_field(name="Warned by", value=ctx.author.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Message ID", value=ctx.message.id, inline=False)
                embed.set_footer(text="Warning Logged at", icon_url=cfg.FOOTER)
                embed.timestamp = datetime.utcnow()
                await log_channel.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"Error: {str(e)}", color=cfg.CLR)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warnings(self, ctx, member: discord.Member):
        """
        Display a member's warnings.
        """
        try:
            self.cursor.execute("SELECT reason FROM warnings WHERE guild_id = ? AND user_id = ?",
                                (ctx.guild.id, member.id))
            warnings = [row[0] for row in self.cursor.fetchall()]
            if warnings:
                embed = discord.Embed(title=f"{member.mention} has {len(warnings)} warning(s):", color=cfg.CLR)
                for warning in warnings:
                    embed.add_field(name="Warning", value=warning, inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{member.mention} has no warnings.", color=cfg.CLR)
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"Error: {str(e)}", color=cfg.CLR)
            await ctx.send(embed=embed)

    commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """
        Kick a member.
        """
        try:
            await member.kick(reason=reason)

            embed = discord.Embed(title="Kick Issued", color=cfg.CLR)
            embed.add_field(name="User Kicked", value=member.mention, inline=False)
            embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text="Kick Issued at", icon_url=cfg.FOOTER)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

            log_channel = self.get_log_channel(ctx.guild.id)
            if log_channel is not None:
                embed = discord.Embed(title="Kick Logged", color=cfg.CLR)
                embed.add_field(name="User Kicked", value=member.mention, inline=False)
                embed.add_field(name="Kicked by", value=ctx.author.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Message ID", value=ctx.message.id, inline=False)
                embed.set_footer(text="Kick Logged at", icon_url=cfg.FOOTER)
                embed.timestamp = datetime.utcnow()
                await log_channel.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"Error: {str(e)}", color=cfg.CLR)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """
        Ban a member.
        """
        try:
            await member.ban(reason=reason)

            embed = discord.Embed(title="Ban Issued", color=cfg.CLR)
            embed.add_field(name="User Banned", value=member.mention, inline=False)
            embed.add_field(name="Banned by", value=ctx.author.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text="Ban Issued at", icon_url=cfg.FOOTER)
            embed.timestamp = datetime.utcnow()
            await ctx.send(embed=embed)

            log_channel = self.get_log_channel(ctx.guild.id)
            if log_channel is not None:
                embed = discord.Embed(title="Ban Logged", color=cfg.CLR)
                embed.add_field(name="User Banned", value=member.mention, inline=False)
                embed.add_field(name="Banned by", value=ctx.author.mention, inline=False)
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="Message ID", value=ctx.message.id, inline=False)
                embed.set_footer(text="Ban Logged at", icon_url=cfg.FOOTER)
                embed.timestamp = datetime.utcnow()
                await log_channel.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"Error: {str(e)}", color=cfg.CLR)
            await ctx.send(embed=embed)

    def get_log_channel(self, guild_id):
        """
        Get the log channel for the guild.
        """
        try:
            self.cursor.execute("SELECT log_channel FROM guilds WHERE guild_id = ?", (guild_id,))
            result = self.cursor.fetchone()
            if result is not None:
                return self.bot.get_channel(result[0])
            return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

async def setup(bot):
    await bot.add_cog(ModCog(bot))