# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ appendices.py ~~~
Code used to reproduce figures contained within the Appendices.
"""

# load packages
import os

from utils.plot_solutions import plot_handler


def plot_appendices(extension='pdf'):
    """Reproduce the appendices: flood map plots of each optimal solution.

    Produce detailed flood maps for each of the optimal solutions discovered by
    the epsilon-MOEA algorithm.

    Parameters
    ----------
    extension : string, optional
        Chosen file extension for the output figure. Default value is 'pdf'.
    """
    # setup file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '..', 'figures')
    data_dir = os.path.join(base_dir, '..', 'sim_data')

    # initialise plot handler and plot flood maps
    plotter = plot_handler(data_dir, output_dir, extension=extension)
    plotter.prepare_and_plot_solutions()

    print(f'Appendices saved to: {output_dir}')


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_appendices(extension='png')