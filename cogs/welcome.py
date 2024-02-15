import discord
from discord.ext import commands
from discord.ui import View, Button
import sqlite3
import config as cfg

class WELCOME(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(cfg.modDB)  # Connect to your SQLite database
        self.cursor = self.conn.cursor()

    @commands.hybrid_command(name='setup-welcome')
    @commands.has_permissions(administrator=True)
    async def setup_welcome(self, ctx: commands.Context):
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await ctx.send("Please enter the welcome channel ID.")
        welcome_channel_id = int((await self.bot.wait_for('message', check=check)).content)

        await ctx.send("Please enter the button1 name.")
        button1_name = (await self.bot.wait_for('message', check=check)).content

        await ctx.send("Please enter the button1 URL.")
        button1_url = (await self.bot.wait_for('message', check=check)).content
#------------------------------------------------------------------------------
        await ctx.send("Please enter the button2 name.")
        button2_name = (await self.bot.wait_for('message', check=check)).content

        await ctx.send("Please enter the button2 URL.")
        button2_url = (await self.bot.wait_for('message', check=check)).content
#------------------------------------------------------------------------------
        await ctx.send("Please enter the button3 name.")
        button3_name = (await self.bot.wait_for('message', check=check)).content

        await ctx.send("Please enter the button3 URL.")
        button3_url = (await self.bot.wait_for('message', check=check)).content
#------------------------------------------------------------------------------
        await ctx.send("Please enter the welcome message description.")
        message_description = (await self.bot.wait_for('message', check=check)).content

        self.cursor.execute("UPDATE guilds SET welcome_channel = ?, button1_name = ?, button1_url = ?, button2_name = ?, button2_url = ?, button3_name = ?, button3_url = ?, message_description = ? WHERE guild_id = ?",
                            (welcome_channel_id, button1_name, button1_url, button2_name, button2_url, button3_name, button3_url, message_description, ctx.guild.id)) #type: ignore
        self.conn.commit()

        await ctx.send("Welcome message setup complete.")

    @commands.command(name='setup-farewell')
    @commands.has_permissions(administrator=True)
    async def setup_farewell(self, ctx: commands.Context):
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        await ctx.send("Please enter the farewell channel ID.")
        farewell_channel_id = int((await self.bot.wait_for('message', check=check)).content)

        self.cursor.execute("UPDATE guilds SET farewell_channel_id = ? WHERE guild_id = ?",
                            (farewell_channel_id, ctx.guild.id)) #type: ignore
        self.conn.commit()

        await ctx.send("Farewell message setup complete.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Fetch the welcome channel ID from the database
        self.cursor.execute("SELECT welcome_channel FROM guilds WHERE guild_id = ?", (member.guild.id,))
        welcome_channel_id = self.cursor.fetchone()[0]

        # Fetch the button details from the database
        self.cursor.execute("SELECT button1_name, button1_url, button2_name, button2_url, button3_name, button3_url FROM guilds WHERE guild_id = ?", (member.guild.id,))
        button1_name, button1_url, button2_name, button2_url, button3_name, button3_url = self.cursor.fetchone()

        # Fetch the message description from the database
        self.cursor.execute("SELECT message_description FROM guilds WHERE guild_id = ?", (member.guild.id,))
        message_description = self.cursor.fetchone()[0]

        embed = discord.Embed(color=cfg.CLR, title="Welcome to our server!")
        button1 = Button(label=button1_name, url=button1_url)
        button2 = Button(label=button2_name, url=button2_url)
        button3 = Button(label=button3_name, url=button3_url)

        view = View()
        view.add_item(button1)
        view.add_item(button2)
        view.add_item(button3)
        embed.description = message_description
        embed.set_footer(text=f'{member.guild.name} | {member.guild.id}', icon_url=member.guild.icon.url) #type: ignore
        channel = self.bot.get_channel(welcome_channel_id)
        await channel.send(content=member.mention, embed=embed, view=view)
        await member.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        # Fetch the farewell channel ID from the database
        self.cursor.execute("SELECT farewell_channel_id FROM guilds WHERE guild_id = ?", (member.guild.id,))
        farewell_channel_id = self.cursor.fetchone()[0]

        description = (f'**{member.name}** just left us.\n'
                       f"We're now **{len(member.guild.members)}** members.\n")
        embed = discord.Embed(
            title='Farewell', description=description, color=cfg.CLR)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(
            text=f'{member.guild.name} | {member.guild.id}', icon_url=member.guild.icon.url) #type: ignore

        channel = self.bot.get_channel(farewell_channel_id)
        await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WELCOME(bot))