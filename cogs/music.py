import discord
from discord.ext import commands
from discord.ui import Button, View
import youtube_dl
from youtubesearchpython import searchYoutube
import lyricsgenius

class MusicPlayer(commands.Cog):
    """Music Player Cog"""
    def __init__(self, bot):
        self.bot = bot
        self.genius = lyricsgenius.Genius('your-genius-token')  # Replace with your Genius token

    @commands.command()
    async def play(self, ctx, *, search):
        """
        Searches for and plays audio from a YouTube search query.
        """
        # Search for music
        results = searchYoutube(search, max_results=1).to_dict()
        url = 'https://www.youtube.com' + results[0]['url_suffix']

        # Connect to voice channel
        channel = ctx.author.voice.channel
        voice_channel = await channel.connect()

        # Download audio
        ydl_opts = {'format': 'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_channel.play(discord.FFmpegPCMAudio(url2))

        # Create view with stop button
        view = StopButtonView(self.bot, voice_channel)
        await ctx.send('Now playing...', view=view)

    @commands.command()
    async def lyrics(self, ctx, *, search):
        """
        Searches for and sends the lyrics of a song.
        """
        song = self.genius.search_song(search)
        await ctx.send(song.lyrics)

class StopButtonView(View):
    """View with a stop button"""
    def __init__(self, bot, voice_channel):
        super().__init__()
        self.bot = bot
        self.voice_channel = voice_channel
        self.add_item(Button(label="Stop", style=discord.ButtonStyle.red, custom_id="stop"))

    @discord.ui.button(label='Stop', style=discord.ButtonStyle.red, custom_id='stop') #type: ignore
    async def stop_button(self, interaction: discord.Interaction):
        """
        Stops the audio playback.
        """
        if self.voice_channel.is_playing():
            self.voice_channel.stop()
        await interaction.response.send_message('Stopped playing.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))