# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_20.py ~~~
Code used to reproduce Figure 20.
"""

# load packages
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import re
import pandas as pd

from utils.utils import read_solutions
from utils.utils import calculate_hypervolume_metric
from utils.utils import natural_keys
from utils.utils import set_plot_defaults


def plot_fig_20(extension='pdf'):
    """Reproduce Figure 20, a comparison of the algorithm convergence rates.

    Comparison between the hyper-volume indicator, labelled as the S-metric,
    per unique simulation for the proposed epsilon-MOEA with respect to the
    NSGA-2 and SPEA-2.

    Parameters
    ----------
    extension : string, optional
        Chosen file extension for the output figure. Default value is 'pdf'.
    """
    set_plot_defaults(mpl)

    # Prepare figure and axes
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    algorithms = ['emoea', 'nsga', 'spea']
    alg_map = {'emoea': 'eMOEA',
               'nsga': 'NSGA',
               'spea': 'SPEA'}
    label_map = {'eMOEA': r'$\epsilon$-MOEA',
                 'NSGA': 'NSGA-II',
                 'SPEA': 'SPEA-2'}
    color_map = {'eMOEA': 'r',
                 'NSGA': 'b',
                 'SPEA': 'g'}

    # calculate a fixed reference point based on the worst objective vector
    cost_max, risk_max = 0, 0  # initialise worst objective vector
    cost_min, risk_min = 0, 0
    for algorithm in algorithms:
        print(f'--- Plotting {algorithm} ---')
        # Locate all solution files for the specified algorithm
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'test_2_data', f'{algorithm}')
        # search all generations for worst objective vector
        pattern = re.compile(r'^Generation_(\d+)_Solutions\.txt$')
        solution_files = [
            os.path.join(data_dir, folder)
            for folder in os.listdir(data_dir) if pattern.match(folder)
        ]
        for solution_file in solution_files:
            solutions = read_solutions(solution_file)
            for solution in solutions:
                cost_max = max(cost_max, solution[0])
                cost_min = min(cost_min, solution[0])
                risk_max = max(risk_max, solution[1])
                risk_min = max(risk_min, solution[1])

    reference_cost = cost_max + 0.1*(abs(cost_max - cost_min))
    reference_risk = risk_max + 0.1*(abs(risk_max - risk_min))
    reference_point = (reference_cost, reference_risk)

    # plot convergence
    for algorithm in algorithms:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, '..', 'test_2_data', f'{algorithm}')
        simulations_file = os.path.join(data_dir, 'unique_simulations.txt')
        sim_data = pd.read_csv(simulations_file, header=None)
        no_sims = sim_data.loc[:, 0]
        s_metrics = []
        pattern = re.compile(r'^Generation_(\d+)_Solutions\.txt$')
        matching_files = [folder for folder in os.listdir(data_dir)
                          if pattern.match(folder)]
        matching_files.sort(key=natural_keys)
        solution_files = [os.path.join(data_dir, folder)
                          for folder in matching_files]
        
        for solution_file in solution_files:
            solutions = read_solutions(solution_file)
            s_metrics.append(calculate_hypervolume_metric(solutions,
                                                          reference_point))
            
        algorithm = alg_map.get(algorithm, algorithm)
        label = label_map.get(algorithm, algorithm)
        
        # Plot the sorted, aligned data
        ax.plot(no_sims, s_metrics, linestyle='dashed',
                color=color_map[algorithm], label=f'{label}')

    # Formatting adjustments
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=9, loc='lower right')

    ax.set_title('Convergence')
    ax.set_xlabel('Number of Unique Simulations', fontsize=10)
    ax.set_ylabel('Convergence Measure (S-metric)', fontsize=10)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_dir = os.path.join(base_dir, '..', 'figures')
    output_path = os.path.join(output_dir, f'Figure_20.{extension}')
    with open(output_path, 'wb') as file:
        fig.savefig(file, format=f'{extension}', dpi=600)

    print(f'Figure 20 saved to: {output_path}')


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_20()