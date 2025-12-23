# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_18.py ~~~
Code used to reproduce Figure 18.
"""

# load packages
import os
import matplotlib.pyplot as plt


def plot_fig_18():
    """Reproduce Figure 18, a comparison of the algorithm convergence rates.

    Performance of the algorithms for varying maximum archive sizes, shown
    through plots of the hyper-volume ratio against the number of fitness
    evaluations.
    """
