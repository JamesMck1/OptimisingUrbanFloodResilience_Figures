# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_21.py ~~~
Code used to reproduce Figure 21.
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
from utils.utils import non_dominated_sort
from utils.utils import set_plot_defaults


def plot_fig_21():
    """Reproduce Figure 21, a comparison of the final solutions.

    Comparison between the final solutions for the three MOEAs after
    self-termination of the eMOEA algorithm. The worst objective vector is used
    as the fixed reference point for the calculation of the performance metric.
    The non-dominated points with respect to the set of all final solutions
    across all algorithms are highlighted with black dots.
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
    sims = []  # initialise a list for the total number of unique sims per alg
    cost_max, risk_max = 0, 0  # initialise worst objective vector
    termination_sims = 0
    for ix, algorithm in enumerate(algorithms):
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
                risk_max = max(risk_max, solution[1])

        simulations_file = os.path.join(data_dir, 'unique_simulations.txt')
        no_sims = pd.read_csv(simulations_file, header=None)

        if termination_sims == 0:  # read the Solutions.txt file for eMOEA
            final_solution_file = os.path.join(data_dir, 'Solutions.txt')
            all_solutions = read_solutions(final_solution_file)
            all_costs, all_risks = zip(*all_solutions)
            termination_sims = no_sims.iloc[-1, 0]
            sims.append(termination_sims)
        else:  # find the solution_file for equal sims for the benchmark algs
            differences = (no_sims[0] - termination_sims).abs()
            closest_index = differences.idxmin()
            closest_sim = no_sims.loc[closest_index, 0]
            sims.append(closest_sim)
            closest_solution_file = os.path.join(
                data_dir, f'Generation_{closest_index}_Solutions.txt')
            all_solutions = read_solutions(closest_solution_file)
            all_costs, all_risks = zip(*all_solutions)

        # filter only non-dominated solutions
        pareto_solutions = non_dominated_sort(all_solutions)
        pareto_costs, pareto_risks = zip(*pareto_solutions)

        # convert costs to £ millions (damages are already in £ millions)
        all_costs = np.array(all_costs)*1e-6
        pareto_costs = np.array(pareto_costs)*1e-6

        algorithm = alg_map.get(algorithm, algorithm)
        label = label_map.get(algorithm, algorithm)
        if algorithm != 'eMOEA':
            ax.scatter(all_costs, all_risks, marker='x', alpha=0.2, s=100,
                    color=color_map[algorithm], label=f'{label}')
        ax.scatter(pareto_costs, pareto_risks, marker='X', alpha=0.6,
                   s=100, color=color_map[algorithm],
                   label=f'{label} (non-dominated)')

    # plot worst objective vector
    cost_max = cost_max*1e-6  # convert to £ millions
    ax.scatter(cost_max, risk_max, marker='v', alpha=0.8, s=150, color='gray',
               label='Worst Objective Vector')
    ax.axvline(cost_max, linestyle='dashed', color='gray', alpha=0.8)
    ax.axhline(risk_max, linestyle='dashed', color='gray', alpha=0.8)

    # Formatting adjustments
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(fontsize=9, loc='lower right')
    ax.yaxis.set_major_locator(MultipleLocator(1))
    ax.xaxis.set_major_locator(MultipleLocator(1))

    ax.set_title('Final Solutions\n'
                 r'$\epsilon$-MOEA'f' simulations = {sims[0]}, '
                 f'NSGA-II simulations = {sims[1]}, '
                 f'SPEA-2 simulations = {sims[2]}')
    ax.set_xlabel('Cost (£ millions)', fontsize=10)
    ax.set_ylabel('Estimated Cost of Damages due to Flooding (£ millions)',
                  fontsize=10)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_dir = os.path.join(base_dir, '..', 'figures')
    output_path = os.path.join(output_dir, 'Figure_21.pdf')
    with open(output_path, 'wb') as file:
        fig.savefig(file, format='pdf', dpi=600)

    print(f'Figure 21 saved to: {output_path}')


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_21()