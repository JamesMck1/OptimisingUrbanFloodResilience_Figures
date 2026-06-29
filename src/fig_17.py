# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_17.py ~~~
Code used to reproduce Figure 17.
"""

# load packages
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import re

from utils.utils import load_mean_S_metric
from utils.utils import natural_keys
from utils.utils import set_plot_defaults


def plot_fig_17(extension='pdf'):
    """Reproduce Figure 17, a comparison of the algorithm convergence rates.

    Performance of the algorithms for varying maximum archive sizes, shown
    through plots of the hyper-volume ratio against the number of fitness
    evaluations.

    Parameters
    ----------
    extension : string, optional
        Chosen file extension for the output figure. Default value is 'pdf'.
    """
    set_plot_defaults(mpl)

    # Locate all convergence data files in the specified folder structure
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, '..', 'test_1_data')
    pattern = re.compile(r'^n = (\d+)$')
    convergence_folders = [
        os.path.join(data_dir, folder)
        for folder in os.listdir(data_dir) if pattern.match(folder)
    ]

    print('Plotting population study from data in the following folders:')
    for folder in convergence_folders:
        print(f'{folder}')

    # Sort in human order for plotting (order of pop size)
    convergence_folders.sort(key=natural_keys)

    # Prepare figure and axes
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    algorithms = ['epsilon MOEA', 'NSGA II', 'SPEA 2']
    alg_map = {'epsilon MOEA': 'eMOEA',
               'NSGA II': 'NSGA',
               'SPEA 2': 'SPEA'}
    label_map = {'eMOEA': r'$\epsilon$-MOEA',
                 'NSGA': 'NSGA-II',
                 'SPEA': 'SPEA-2'}
    for ix, algorithm in enumerate(algorithms):
        print(f'--- Plotting {algorithm} ---')
        ax = axes[ix]
        # Custom labelling
        algorithm = alg_map.get(algorithm, algorithm)

        plot_title = label_map.get(algorithm, algorithm)
        ax.set_title(f'{plot_title}', fontsize=12)
        ax.set_xlabel('Unique Simulations', fontsize=10)
        if ix == 0:
            # Set shared y-axis label
            ax.set_ylabel('S-metric (%)', fontsize=10)

        # Colors and linestyles for each population size
        pop_sizes = {'12': 'L', '24': '2L',
                     '36': r'$|P|$', '72': r'$|2P|$'}
        # Set specific color schemes per algorithm
        if algorithm == 'eMOEA':
            colors = {'12': 'lightcoral', '24': 'indianred',
                      '36': 'firebrick', '72': 'darkred'}
        elif algorithm == 'NSGA':
            colors = {'12': 'lightskyblue', '24': 'cornflowerblue',
                      '36': 'royalblue', '72': 'darkblue'}
        elif algorithm == 'SPEA':
            colors = {'12': 'lightgreen', '24': 'mediumseagreen',
                      '36': 'forestgreen', '72': 'darkgreen'}
        linestyles = {'12': 'solid', '24': 'dashed',
                      '36': 'dotted', '72': 'dashdot'}

        # Loop through each folder and plot the S-metric for each algorithm
        for folder in convergence_folders:
            print(os.path.basename(folder))
            match = pattern.search(os.path.basename(folder))
            pop = match.group(1)
            pop_label = pop_sizes[f'{pop}']
            color = colors[f'{pop}']
            linestyle = linestyles[f'{pop}']

            file_path = os.path.join(folder, f"{algorithm} (mean).txt")
            target_simulations, mean_S_metric_data = load_mean_S_metric(
                file_path)

            # Plot mean S-metric data
            ax.plot(target_simulations, mean_S_metric_data,
                    label=pop_label, color=color, linestyle=linestyle)

            # Formatting adjustments
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.legend(fontsize=9)
            ax.yaxis.set_major_locator(MultipleLocator(10))

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_dir = os.path.join(base_dir, '..', 'figures')
    output_path = os.path.join(output_dir, f'Figure_17.{extension}')
    with open(output_path, 'wb') as file:
        fig.savefig(file, format=f'{extension}', dpi=600)

    print(f'Figure 17 saved to: {output_path}')


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_17()