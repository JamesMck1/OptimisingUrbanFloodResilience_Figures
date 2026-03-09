# -*- coding: utf-8 -*-
"""
Created on Mon Dec 22 14:23:35 2025.

@author: James Mckenna

~~~ run.py ~~~
Code used to reproduce Figures 16, 17, 18, 20, 21, 22 & 23.
"""

import sys
import os

# adjust sys.path for imports
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, src_path)

from src.fig_16 import plot_fig_16
from src.fig_17 import plot_fig_17
from src.fig_18 import plot_fig_18
from src.fig_20 import plot_fig_20
from src.fig_21 import plot_fig_21
from src.fig_22 import plot_fig_22
from src.fig_23 import plot_fig_23

# reproduce plots
plot_fig_16()
plot_fig_17()
plot_fig_18()
plot_fig_20()
plot_fig_21()
plot_fig_22()
plot_fig_23()