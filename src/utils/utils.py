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