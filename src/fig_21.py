# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ fig_21.py ~~~
Code used to reproduce Figure 21.
"""

# load packages
import os
import matplotlib.pyplot as plt


def plot_fig_21():
    """Reproduce Figure 21, a comparison of the algorithm convergence rates.

    Comparison between the hyper-volume indicator, labelled as the S-metric,
    per unique simulation for the proposed epsilon-MOEA with respect to the
    NSGA-2 and SPEA-2.
    """
