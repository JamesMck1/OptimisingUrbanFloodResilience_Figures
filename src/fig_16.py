# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_16.py ~~~
Code used to reproduce Figure 16.
"""

# load packages
import os
import numpy as np
import matplotlib.pyplot as plt


def plot_fig_16():
    """Reproduce Figure 16, a plot of the feasible objective space.

    A plot showing all 4096 feasible objective vectors for the 12 zonal feature
    test scenario. Pareto optimal vectors are highlighted in red with dominated
    vectors shown in grey.
    """
    # load data
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'data')

    feasible_data = np.loadtxt(os.path.join(data_dir, 'All_data.txt'),
                               dtype=float, skiprows=1)
    print(f'Loaded {feasible_data.shape[0]} Feasible Objective vectors.')
    pareto_data = np.loadtxt(os.path.join(data_dir, 'Pareto_data.txt'),
                             dtype=float, skiprows=1)
    print(f'Loaded {pareto_data.shape[0]} Pareto-optimal vectors.')

    fig, ax = plt.subplots(figsize=(10, 6))  # initialise figure

    # plot all feasible objective vectors
    ax.scatter(
        feasible_data[:, 0], feasible_data[:, 1],
        color='gray',
        marker='x',
        s=50,
        alpha=0.6,
        label='Feasible Objective Vectors'
    )

    # plot Pareto-front
    ax.scatter(
        pareto_data[:, 0], pareto_data[:, 1],
        color='red',
        marker="*",
        s=150,
        label='Pareto Optimal Vectors'
    )

    ax.set_title('Feasible Objective Space')
    ax.set_xlabel('Implementation Cost (£ millions)')
    ax.set_ylabel('Number of buildings at high risk of flooding')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.show()

    output_dir = os.path.join(base_dir, '..', 'figures')
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    file_path = os.path.join(output_dir, 'Figure_16.png')

    with open(file_path, 'wb') as file:
        fig.savefig(file, format='png')

    return feasible_data, pareto_data


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_16()
