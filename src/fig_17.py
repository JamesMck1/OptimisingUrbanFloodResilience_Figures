# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_17.py ~~~
Code used to reproduce Figure 17.
"""

# load packages
import os
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import re

from utils.utils import load_mean_S_metric
from utils.utils import natural_keys
from utils.utils import set_plot_defaults


def plot_fig_17():
    """Reproduce Figure 17, a comparison of the algorithm convergence rates.

    Comparison between the hyper-volume ratio versus the number of fitness
    evaluations for the three studied MOEAs with different maximum population
    sizes.
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

    # Sort in human order for plotting (order of pop size)
    convergence_folders.sort(key=natural_keys)

    # Prepare figure and axes
    num_plots = len(convergence_folders)
    plots_per_col = int(0.5*num_plots)
    fig, axs = plt.subplots(plots_per_col, 2, figsize=(18, 1.5*num_plots),
                            sharex=True)
    
    pop_sizes = {'0': 'L',
                 '1': '2L',
                 '2': r'$|P|$',
                 '3': r'$|2P|$'}
    
    # Loop through each folder and plot the S-metric for each algorithm
    for idx, folder in enumerate(convergence_folders):
        ax = axs[(idx-int(np.floor(idx/plots_per_col))*plots_per_col,
                    int(np.floor(idx/plots_per_col)))]

        ax.set_title(f'P = {pop_sizes[f"{idx}"]}', fontsize=12)
        ax.set_ylabel('S-metric (%)', fontsize=10)

        # Colors and linestyles for each algorithm
        colors = {'eMOEA': 'red', 'NSGA': 'blue', 'SPEA': 'green'}
        linestyles = {'eMOEA': 'solid', 'NSGA': 'dashed', 'SPEA': 'dotted'}

        for algorithm, color in colors.items():
            # Path to the S-metric data file for this algorithm
            file_path = os.path.join(folder, f"{algorithm} (mean).txt")
            if os.path.exists(file_path):
                target_simulations, mean_S_metric_data = load_mean_S_metric(
                     file_path)

                # Custom labelling
                label_map = {'eMOEA': r'$\epsilon$-MOEA',
                                'NSGA': 'NSGA-II',
                                'SPEA': 'SPEA-2'}
                plot_label = label_map.get(algorithm, algorithm)

                # Plot mean S-metric data
                ax.plot(target_simulations, mean_S_metric_data,
                        label=plot_label, color=color,
                        linestyle=linestyles[algorithm])
                
        # plot self-termination time
        file_path = os.path.join(folder, "eMOEA termination.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Unable to find {file_path}.')
        termination_times = []
        with open(file_path, 'r') as f:
            next(f)

            for line in f:
                row = line.strip().split('\t')
                if row[0] == 'Average':
                        continue
                try:
                    t_val = float(row[1]) 
                    termination_times.append(t_val)
                except (ValueError, IndexError):
                    pass

        if termination_times:
            average_t = np.mean(termination_times)
            std_dev = np.std(termination_times)
            ax.axvline(average_t, color='c', linestyle='dashed',
                        linewidth=2, alpha=0.75, label='Avg. Termination')
            ax.axvspan(average_t - std_dev, average_t + std_dev,
                        color='c', alpha=0.2, linewidth=0)

        # Formatting adjustments
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(fontsize=9)
        ax.yaxis.set_major_locator(MultipleLocator(10))

    # Set common x-label for the shared x-axis
    axs[(plots_per_col-1, 0)].set_xlabel('Unique Simulations', fontsize=10)
    axs[(plots_per_col-1, 1)].set_xlabel('Unique Simulations', fontsize=10)

    # Adjust layout and save
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    output_dir = os.path.join(base_dir, '..', 'figures')
    output_path = os.path.join(output_dir, 'Figure_17.pdf')
    with open(output_path, 'wb') as file:
        fig.savefig(file, format='pdf', dpi=600)

    print(f'Figure 17 saved to: {output_path}')

    return target_simulations, mean_S_metric_data, termination_times


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    test = plot_fig_17()