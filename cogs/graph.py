import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import numpy as np
from utils.graphGen import graphGen

class GraphCog(commands.Cog):
    """
    A simple cog that includes a command to generate a graph from x and y values and send it as an image.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def graph(self, ctx, *values: float):
        """
        Generate a graph from x and y values and send it as an image.

        Args:
            ctx (commands.Context): The context object for the command.
            *values (float): The x and y values for the graph. Should be in the format x1 y1 x2 y2 ...

        Returns:
            None
        """
        # Generate the graph
        graphGen.plotGraph(values)

        # Send the image
        await ctx.send(file=discord.File('assets/plot.png'))

    @commands.command()
    async def cartesianPlane(self, ctx, *values: float):
        """
        Generate a graph on a cartesian plane from x and y values and send it as an image.

        Args:
            ctx (commands.Context): The context object for the command.
            *values (float): The x and y values for the graph. Should be in the format x1 y1 x2 y2 ...

        Returns:
            None
        """
        # Generate the graph
        graphGen.generateCartesianPlane(values)

        # Send the image
        await ctx.send(file=discord.File('assets/plot.png'))

async def setup(bot):
   await bot.add_cog(GraphCog(bot))