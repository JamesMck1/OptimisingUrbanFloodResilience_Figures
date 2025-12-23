# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_20.py ~~~
Code used to reproduce Figure 20.
"""

# load packages
import os
import matplotlib.pyplot as plt


def plot_fig_20():
    """Reproduce Figure 20, a comparison of the final solutions.

    Comparison between the final solutions for the three MOEAs after
    $\approx$3000 simulations. The worst objective vector is used as the fixed
    reference point for the calculation of the performance metric. The
    non-dominated points with respect to the set of all final solutions across
    all algorithms are highlighted with black dots.
    """
