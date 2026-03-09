# Multi-Objective Evolutionary Algorithms for Flood Risk Mitigation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.
python.org/downloads/)

This repository contains the data processing and figure generation code used in 
the paper:
> **"Optimising Urban Flood Resilience"** > *J.McKenna, C.Illiadis & V.Glenis > Submitted to *Water Resources Research* (2026).

## Overview

This repository provides the Python codebase to reproduce the comparative
analysis of three Multi-Objective Evolutionary Algorithms (MOEAs):
1. **$\epsilon$-MOEA** (Proposed algorithm)
2. **NSGA-II** (Benchmark algorithm)
3. **SPEA-2** (Benchmark algorithm)

The algorithms are applied to a spatial flood risk management problem. The 
objectives minimised are the **Implementation Cost (£ millions)** and the 
**Number of Buildings at High Risk of Flooding / Estimated Cost of Damages due
to Flooding**. The code evaluates algorithm performance based on Pareto
dominance, self-termination efficiency, and convergence via the Hypervolume
Indicator (S-metric).

## Repository Structure

The repository is structured to allow seamless reproduction of all figures from
the root directory. Please ensure your data directories are populated before
running the scripts:

```text
├── run.py                    # Master script to execute all figure generation
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── utils.py          # Helper functions
│   ├── fig_16.py             # Plots the feasible objective space
│   ├── fig_17.py             # Compares algorithm convergence rates (S-metric)
│   ├── fig_18.py             # Performance for varying maximum archive sizes
│   ├── fig_20.py             # Final solutions comparison 1
│   ├── fig_21.py             # Final solutions comparison 2
│   ├── fig_22.py             # S-metric convergence per unique simulation
│   └── fig_23.py             # Comparative sub-plots of final solutions
├── test_1_data/              # Data for Figures 16, 17, and 18
├── test_2_data/              # Data for Figures 20, 21, 22, and 23
└── figures/                  # Automatically generated output folder for plots
