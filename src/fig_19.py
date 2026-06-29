# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_19.py ~~~
Code used to reproduce Figure 19.
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


def plot_fig_19(extension='pdf'):
    """Reproduce Figure 19, a comparison of the final solutions.

    Comparison between the final solutions for the three MOEAs. Sub-figure (a)
    shows the final solutions after self-termination of the eMOEA algorithm
    (~1000 simulations). Sub-figure (b) shows a comparison between the final
    solutions after the benchmark algorithms are evolved further (~3000
    simulations). The worst objective vector is used as the fixed reference
    point for the calculation of the performance metric. The non-dominated
    points with respect to the set of all final solutions across all algorithms
    are highlighted with black dots.

    Parameters
    ----------
    extension : string, optional
        Chosen file extension for the output figure. Default value is 'pdf'.
    """
    set_plot_defaults(mpl)

    # Prepare figure and axes
    fig, (ax_1, ax_2) = plt.subplots(2, 1, figsize=(12, 12))
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
    final_sims = []  # list for the total number of unique sims per alg
    cost_max, risk_max = 0, 0  # initialise worst objective vector
    termination_sims = 0
    for algorithm in algorithms:
        """ --- Sub-plot (a) --- """
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
        # if algorithm != 'eMOEA':
        #     ax_1.scatter(all_costs, all_risks, marker='x', alpha=0.2, s=100,
        #                  color=color_map[algorithm], label=f'{label}')
        ax_1.scatter(pareto_costs, pareto_risks, marker='X', alpha=0.6,
                     s=100, color=color_map[algorithm],
                     label=f'{label} (non-dominated)')
        
        """ --- Sub-plot (b) --- """
        final_solution_file = os.path.join(data_dir, 'Solutions.txt')
        all_solutions = read_solutions(final_solution_file)
        all_costs, all_risks = zip(*all_solutions)

        # filter only non-dominated solutions
        pareto_solutions = non_dominated_sort(all_solutions)
        pareto_costs, pareto_risks = zip(*pareto_solutions)

        # convert costs to £ millions (damages are already in £ millions)
        all_costs = np.array(all_costs)*1e-6
        pareto_costs = np.array(pareto_costs)*1e-6

        algorithm = alg_map.get(algorithm, algorithm)
        label = label_map.get(algorithm, algorithm)
        # if algorithm != 'eMOEA':
        #     ax_2.scatter(all_costs, all_risks, marker='x', alpha=0.2, s=100,
        #                  color=color_map[algorithm], label=f'{label}')
        ax_2.scatter(pareto_costs, pareto_risks, marker='X', alpha=0.6,
                     s=100, color=color_map[algorithm],
                     label=f'{label} (non-dominated)')
        final_sims.append(no_sims.iloc[-1, 0])

    # plot worst objective vector
    cost_max = cost_max*1e-6  # convert to £ millions
    for ax in [ax_1, ax_2]:
        ax.scatter(cost_max, risk_max, marker='v', alpha=0.8, s=150,
                   color='gray', label='Worst Objective Vector')
        ax.axvline(cost_max, linestyle='dashed', color='gray', alpha=0.8)
        ax.axhline(risk_max, linestyle='dashed', color='gray', alpha=0.8)

        # Formatting adjustments
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(fontsize=9, loc='lower right')
        ax.yaxis.set_major_locator(MultipleLocator(1))
        ax.xaxis.set_major_locator(MultipleLocator(1))
        ax.set_xlabel('Cost (£ millions)', fontsize=10)
        ax.set_ylabel('Estimated Cost of Damages due to Flooding (£ millions)',
                      fontsize=10)

    # first sub-plot
    ax_1.set_title('Solutions at Self-Termination\n'
                   r'$\epsilon$-MOEA'f' simulations = {sims[0]}, '
                   f'NSGA-II simulations = {sims[1]}, '
                   f'SPEA-2 simulations = {sims[2]}')
    ax_2.set_title('Final Solutions\n'
                   r'$\epsilon$-MOEA'f' simulations = {final_sims[0]}, '
                   f'NSGA-II simulations = {final_sims[1]}, '
                   f'SPEA-2 simulations = {final_sims[2]}')
    
    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_dir = os.path.join(base_dir, '..', 'figures')
    output_path = os.path.join(output_dir, f'Figure_19.{extension}')
    with open(output_path, 'wb') as file:
        fig.savefig(file, format=f'{extension}', dpi=600)

    print(f'Figure 19 saved to: {output_path}')


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_19()