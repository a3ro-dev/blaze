import discord
from discord.ext import commands
from discord.ui import View, Button
import sqlite3
import config as cfg


class Greeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect(cfg.modDB)  # Connect to your SQLite database
        self.cursor = self.conn.cursor()

    @commands.hybrid_command(name='setup-welcome')
    @commands.has_permissions(administrator=True)
    async def setup_welcome(self, ctx: commands.Context):
        def check(m):
            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id

        embed = discord.Embed(title="Please enter the welcome channel ID.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        welcome_channel_id = int((await self.bot.wait_for('message', check=check)).content)

        embed = discord.Embed(title="Please enter the button1 name.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button1_name = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the button1 URL.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button1_url = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the button2 name.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button2_name = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the button2 URL.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button2_url = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the button3 name.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button3_name = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the button3 URL.", color=cfg.CLR)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        button3_url = (await self.bot.wait_for('message', check=check)).content

        embed = discord.Embed(title="Please enter the welcome message description.", color=cfg.CLR)
        embed.add_field(name="{memberNUMBER}", value="Use this to display the number of members in the server at the "
                                                     "time the member joined. Example: `We are now {memberNUMBER} "
                                                     "members strong!`", inline=False)
        embed.add_field(name="{memberNAME}", value="Use this to display the user's name. Example: `Welcome {"
                                                   "memberNAME} to our server!`", inline=False)
        embed.add_field(name="{guildNAME}", value="Use this to display the server name. Example: `You have joined {"
                                                  "guildNAME}.`", inline=False)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        embed.set_footer(text=cfg.FOOTER)
        await ctx.send(embed=embed)
        message_description = (await self.bot.wait_for('message', check=check)).content

        self.cursor.execute(
            "INSERT OR REPLACE INTO guilds (guild_id, welcome_channel, button1_name, button1_url, button2_name, button2_url, button3_name, button3_url, message_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ctx.guild.id, welcome_channel_id, button1_name, button1_url, button2_name, button2_url, button3_name,
             button3_url,
             message_description))  # type: ignore
        self.conn.commit()

        # Fetch the values from the database
        self.cursor.execute(
            "SELECT welcome_channel, button1_name, button1_url, button2_name, button2_url, button3_name, button3_url, message_description FROM guilds WHERE guild_id = ?",
            (ctx.guild.id,))

        result = self.cursor.fetchone()

        if result is not None:
            welcome_channel_id, button1_name, button1_url, button2_name, button2_url, button3_name, button3_url, message_description = result
            print(
                f"Updated guild {ctx.guild.id} with welcome_channel_id {welcome_channel_id}, button1_name {button1_name}, button1_url {button1_url}, button2_name {button2_name}, button2_url {button2_url}, button3_name {button3_name}, button3_url {button3_url}, message_description {message_description}")
        else:
            print(f"No data found for guild {ctx.guild.id}")

        await ctx.send("Welcome message setup complete.")

    # @commands.command(name='setup-farewell')
    # @commands.has_permissions(administrator=True)
    # async def setup_farewell(self, ctx: commands.Context):
    #     def check(m):
    #         return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
    #
    #     await ctx.send("Please enter the farewell channel ID.")
    #     farewell_channel_id = int((await self.bot.wait_for('message', check=check)).content)
    #
    #     self.cursor.execute("UPDATE guilds SET farewell_channel_id = ? WHERE guild_id = ?",
    #                         (farewell_channel_id, ctx.guild.id))  # type: ignore
    #     self.conn.commit()
    #
    #     await ctx.send("Farewell message setup complete.")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Fetch the welcome channel ID from the database
        self.cursor.execute("SELECT welcome_channel FROM guilds WHERE guild_id = ?", (member.guild.id,))
        fetch_result = self.cursor.fetchone()
        welcome_channel_id = fetch_result[0] if fetch_result is not None else None

        # Fetch the button details from the database
        self.cursor.execute(
            "SELECT button1_name, button1_url, button2_name, button2_url, button3_name, button3_url FROM guilds WHERE guild_id = ?",
            (member.guild.id,))
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
        embed.set_footer(text=f'{member.guild.name} | {member.guild.id}',
                         icon_url=member.guild.icon.url if member.guild.icon else None)  # type: ignore
        channel = self.bot.get_channel(welcome_channel_id)
        await channel.send(content=member.mention, embed=embed, view=view)
        await member.send(embed=embed, view=view)

    # @commands.Cog.listener()
    # async def on_member_remove(self, member: discord.Member):
    #     # Fetch the farewell channel ID from the database
    #     self.cursor.execute("SELECT farewell_channel_id FROM guilds WHERE guild_id = ?", (member.guild.id,))
    #     farewell_channel_id = self.cursor.fetchone()[0]
    #
    #     description = (f'**{member.name}** just left us.\n'
    #                    f"We're now **{len(member.guild.members)}** members.\n")
    #     embed = discord.Embed(
    #         title='Farewell', description=description, color=cfg.CLR)
    #     embed.timestamp = discord.utils.utcnow()
    #     embed.set_footer(
    #         text=f'{member.guild.name} | {member.guild.id}', icon_url=member.guild.icon.url)  # type: ignore
    #
    #     channel = self.bot.get_channel(farewell_channel_id)
    #     await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Greeting(bot))
