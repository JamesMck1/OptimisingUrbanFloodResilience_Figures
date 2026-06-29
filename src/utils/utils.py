# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ utils.py ~~~
Utility/helper functions for plotting.
"""

# load packages
import numpy as np
import re
import pandas as pd
import os


def set_plot_defaults(mpl):
    """Set the formatting for high-quality output."""
    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['ps.fonttype'] = 42
    mpl.rcParams['font.family'] = 'Arial'

def load_mean_S_metric(file_path):
    """Load mean S-metric data from a .txt file."""
    target_simulations = []
    mean_S_metric_data = []

    with open(file_path, 'r') as f:
        # Skip the header
        next(f)

        # Read each line of data
        for line in f:
            sim, s_metric = line.strip().split('\t')
            target_simulations.append(int(sim))
            mean_S_metric_data.append(float(s_metric))

    # Convert lists to numpy arrays for further processing
    return np.array(target_simulations), np.array(mean_S_metric_data)


def atoi(text):
    """Return an integer if text is a digit."""
    return int(text) if text.isdigit() else text


def natural_keys(text):
    """Sorting of text in a human order (alphabetical + ascending numerical).

    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    """
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def read_solutions(solutions_file):
    """Read a Solutions.txt file to obtain front data (cost and risk)."""
    if not os.path.exists(solutions_file):
        print("Solutions.txt not found at: %s", solutions_file)

    else:
        # eMOEA produces a tab-separated file
        try:
            # df = pd.read_csv(solutions_file, sep='\t')
            df = pd.read_csv(
                solutions_file, 
                sep='\t', 
                dtype={
                    'Genotype': str, 
                    'Pavements': str, 
                    'RainGardens': str, 
                    'GreenAreas': str
                }
            )

            # Verify the required columns exist
            if 'Cost' in df.columns and 'Risk' in df.columns:
                # Zip the two columns together and convert to a list of tuples
                return list(zip(df['Cost'], df['Risk']))
            else:
                print("Error: 'Cost' or 'Risk' columns not found in the file.")
                return []
            
        except pd.errors.EmptyDataError:
            print("Solutions.txt is empty.")
            df = pd.DataFrame()


def non_dominated_sort(solutions):
    """Perform a non-dominated sort."""
    non_dominated = []

    for i, solution in enumerate(solutions):
        dominated = False
        for j, other_solution in enumerate(solutions):
            if i != j:
                # Check if other_solution dominates solution
                if ((other_solution[0] <= solution[0] and
                        other_solution[1] <= solution[1]) and
                        (other_solution[0] < solution[0] or
                         other_solution[1] < solution[1])):
                    dominated = True
                    break
        if not dominated:
            non_dominated.append(solution)

    return non_dominated


def calculate_hypervolume_metric(solutions, reference_point):
    """Calculate the hypervolume metric for a set of non-dominated points"""
    # Sort solutions by cost (ascending order)
    solutions.sort(key=lambda s: s[0])  # Sort by the first objective (cost)
    solutions = non_dominated_sort(solutions)
    solutions.sort(key=lambda s: s[0])  # Sort by the first objective (cost)
    
    x_ref, y_ref = reference_point
    hypervolume = 0

    # First point contribution
    x0, y0 = solutions[0]
    hypervolume += abs(x_ref - x0) * abs(y_ref - y0)

    # Iterate through sorted solutions and calculate area contributions
    for i in range(1, len(solutions)):
        x1, y1 = solutions[i-1]
        x2, y2 = solutions[i]
        # Area of the rectangle formed by two consecutive points
        hypervolume += abs(x_ref - x2) * abs(y1 - y2)

    return hypervolume