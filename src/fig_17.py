# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_17.py ~~~
Code used to reproduce Figure 17.
"""

# load packages
import os
import matplotlib.pyplot as plt


def plot_fig_17():
    """Reproduce Figure 17, a comparison of the algorithm convergence rates.

    Comparison between the hyper-volume ratio versus the number of fitness
    evaluations for the three studied MOEAs with different maximum archive
    sizes.
    """
