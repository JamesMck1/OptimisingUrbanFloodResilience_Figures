# Multi-Objective Evolutionary Algorithms for Flood Risk Mitigation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.
python.org/downloads/)

This repository contains the data processing and figure generation code used in 
the paper:
> **"Optimising Urban Flood Resilience"**
> *J.McKenna, C.Illiadis & V.Glenis*
> Submitted to *Advances in Engineering Software* (2026).

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
│   │   └── binary_encoding.py     # Genotype <-> phenotype mapping
│   │   └── plot_solutions.py      # Flood map plotting
│   │   └── utils.py               # Other helper functions
│   ├── appendices.py         # Plots the figures in the appendices
│   ├── fig_15.py             # Plots the feasible objective space
│   ├── fig_16.py             # Compares algorithm convergence rates (S-metric)
│   ├── fig_17.py             # Performance for varying maximum archive sizes
│   ├── fig_19.py             # Final solutions comparison
│   ├── fig_20.py             # S-metric convergence per unique simulation
│   ├── fig_22.py             # 
├── sim_data/                 # Data for Appendices
├── test_1_data/              # Data for Figures 15, 16, and 17
├── test_2_data/              # Data for Figures 19 and 20
└── figures/                  # Automatically generated output folder for plots
