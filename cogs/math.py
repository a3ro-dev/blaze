from discord.ext import commands
from discord import ui, ButtonStyle
import config as cfg
import math
import numpy as np 
from scipy import integrate

class MathsButton(ui.Button):
    def __init__(self, result, operation):
        super().__init__(style=ButtonStyle.green, label="Show Result")
        self.result = result
        self.operation = operation

    async def callback(self, interaction):
        await interaction.response.send_message(f"The result of {self.operation} is {self.result}", ephemeral=True)

class MathsView(ui.View):
    def __init__(self, result, operation):
        super().__init__()
        self.add_item(MathsButton(result, operation))

class Maths(commands.Cog):
    """A cog for mathematical operations."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def add(self, ctx, *numbers: float):
        """
        Adds multiple numbers together.

        Args:
            *numbers (float): The numbers to be added.
        """
        result = sum(numbers)
        await ctx.send(f"The sum of {', '.join(str(num) for num in numbers)} is {result}.", view=MathsView(result, "addition"))

    @commands.command()
    async def equation(self, ctx, *, equation: str):
        """
        Evaluates an equation.

        Args:
            equation (str): The equation to evaluate.
        """
        # Sanitize the equation and only allow certain characters
        equation = ''.join(ch for ch in equation if ch in '0123456789.+-*/() ')
        result = eval(equation)
        await ctx.send(f"The result of the equation '{equation}' is {result}.", view=MathsView(result, "equation evaluation"))

    @commands.command()
    async def quadratic(self, ctx, a: float, b: float, c: float):
        """
        Solves a quadratic equation.

        Args:
            a (float): The coefficient of x^2.
            b (float): The coefficient of x.
            c (float): The constant term.
        """
        discriminant = b**2 - 4*a*c
        if discriminant < 0:
            result = "The quadratic equation has no real solutions."
        elif discriminant == 0:
            result = f"The quadratic equation has one real solution: {-b / (2*a)}"
        else:
            result = f"The quadratic equation has two real solutions: {(-b + math.sqrt(discriminant)) / (2*a)}, {(-b - math.sqrt(discriminant)) / (2*a)}"
        await ctx.send(result, view=MathsView(result, "quadratic equation solving"))

    @commands.command()
    async def profit(self, ctx, cost_price: float, selling_price: float):
        """
        Calculates the profit from a transaction.

        Args:
            cost_price (float): The cost price of the item.
            selling_price (float): The selling price of the item.
        """
        result = selling_price - cost_price
        await ctx.send(f"The profit from the transaction is {result}.", view=MathsView(result, "profit calculation"))

    @commands.command()
    async def solve_linear_system(self, ctx, *coefficients: float):
        """
        Solves a system of linear equations.

        Args:
            *coefficients (float): The coefficients of the equations, given as a flat list.
        """
        matrix = np.array(coefficients).reshape(-1, int(len(coefficients)**0.5))
        coefficients, constants = tuple(matrix[:, :-1]), tuple(matrix[:, -1])
        result = np.linalg.solve(coefficients, constants)
        await ctx.send(f"The solution to the system of linear equations is {result}.", view=MathsView(result, "linear system solving"))

    @commands.command()
    async def integrate(self, ctx, *, function: str):
        """
        Performs numerical integration of a function.

        Args:
            function (str): The function to integrate, given as a string.
        """
        # Define the function to integrate
        def f(x):
            return eval(function)

        result, error = integrate.quad(f, 0, 1)
        await ctx.send(f"The result of the numerical integration of the function '{function}' is {result}.", view=MathsView(result, "numerical integration"))

async def setup(bot):
    await bot.add_cog(Maths(bot))
