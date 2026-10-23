# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ run.py ~~~
Code used to reproduce Figures 16, 17, 18, 20, 21, 22 & 23 and Supplementary
Figures 1-5.
"""

from src.fig_15 import plot_fig_15
from src.fig_16 import plot_fig_16
from src.fig_17 import plot_fig_17
from src.fig_19 import plot_fig_19
from src.fig_20 import plot_fig_20
from src.supplementary_figures import plot_supplementary_figures

################################################################################
# Plotting
################################################################################

extension = 'pdf'

# reproduce plots
plot_fig_15(extension)
plot_fig_16(extension)
plot_fig_17(extension)
plot_fig_19(extension)
plot_fig_20(extension)
plot_supplementary_figures(extension)