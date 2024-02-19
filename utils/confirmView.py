import discord
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