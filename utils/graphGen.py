import matplotlib.pyplot as plt
import numpy as np

class graphGen:

    @staticmethod
    def generateCartesianPlane(values):
        """
        Generate a graph from x and y values and save it as an image.

        Args:
            values (tuple of float): The x and y values for the graph. Should be in the format x1 y1 x2 y2 ...

        Returns:
            None
        """
        # Convert the values to a numpy array
        values = np.array(values, dtype=float)

        # Split the array into x and y values
        x = values[::2]
        y = values[1::2]

        # Create the plot
        plt.plot(x, y)

        # Save the plot as an image
        plt.savefig('assets/plot.png')
        plt.close()

    @staticmethod
    def plotGraph(values):
        """
        Generate a graph from x and y values and save it as an image.

        Args:
            values (tuple of float): The x and y values for the graph. Should be in the format x1 y1 x2 y2 ...

        Returns:
            None
            """
        # Convert the values to a numpy array
        values = np.array(values, dtype=float)

        # Split the array into x and y values
        x = values[::2]
        y = values[1::2]

        # Create the plot
        plt.plot(x, y)

        # Save the plot as an image
        plt.savefig('assets/plot.png')
        plt.close()

        # Usage:
        # generate_graph((1.0, 2.0, 3.0, 4.0, 5.0, 6.0))