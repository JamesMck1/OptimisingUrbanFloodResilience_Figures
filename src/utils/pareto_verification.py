# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 09:29:06 2025.

@author: James Mckenna

~~~ pareto_verification.py ~~~
Code verify if a Pareto set contains only Pareto-optimal vectors.
"""

# load packages
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def pareto_verification(file_path):
    """Verify if a given set is truly Pareto optimal."""
    df = pd.read_csv(
        file_path,
        sep='\t',
        header=1,
        names=['cost', 'risk'],
        dtype={'cost': float, 'risk': float}
    )
    sorted_df = df.sort_values(by=['cost', 'risk'])

    pareto_front = []
    feasible_vectors = []

    previous_cost = -1
    previous_risk = np.inf
    for i, row in sorted_df.iterrows():
        cost_diff = row['cost'] - previous_cost
        risk_diff = previous_risk - row['risk']

        if cost_diff <= 0:
            feasible_vectors.append(row)
            print(f'Vector {i} is not Pareto optimal:\n',
                  f'dx = {cost_diff:.4f}, dy = {risk_diff:.4f}')

        elif risk_diff <= 0:
            feasible_vectors.append(row)
            print(f'Vector {i} is not Pareto optimal',
                  f'dx = {cost_diff:.4f}, dy = {risk_diff:.4f}')

        elif cost_diff > 0 and risk_diff > 0:
            pareto_front.append(row)
            previous_cost = row['cost']
            previous_risk = row['risk']
            print(f'Vector {i} is Pareto optimal')

    print('\n--- Summary ---\n',
          f'Pareto optimal vectors = {len(pareto_front)}\n'
          f'Feasible vectors = {len(feasible_vectors)}\n')

    fig, ax = plt.subplots(figsize=(10, 6))  # initialise figure

    feasible_df = pd.DataFrame(feasible_vectors)
    pareto_df = pd.DataFrame(pareto_front)

    # plot all feasible objective vectors
    try:
        ax.scatter(
            feasible_df['cost'], feasible_df['risk'],
            color='gray',
            marker='x',
            s=50,
            alpha=0.6,
            label='Feasible Objective Vectors'
        )
    except:
        print('No feasible vectors (all vectors are Pareto-optimal).')

    # plot Pareto-front
    ax.scatter(
        pareto_df['cost'], pareto_df['risk'],
        color='red',
        marker="*",
        s=150,
        label='Pareto Optimal Vectors'
    )

    ax.set_title('Feasible Objective Space')
    ax.set_xlabel('Implementation Cost (£ millions)')
    ax.set_ylabel('Number of buildings at high risk of flooding')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.show()

    return pareto_df, feasible_df


###############################################################################
# Testing
###############################################################################


if __name__ == "__main__":

    dir_new = r'C:\Users\njm357\GitHub\WRR_Figures\data\Archive\New\50yr'
    dir_old = r'C:\Users\njm357\GitHub\WRR_Figures\data\Archive\Old\50yr'
    dir_incorrect = r'C:\Users\njm357\GitHub\WRR_Figures\data\Archive\Incorrect\50yr'
    dir_original = r'C:\Users\njm357\GitHub\WRR_Figures\data\Archive\50yr'

    file_path = os.path.join(dir_original, 'Pareto_data.txt')

    pareto_df, feasible_df = pareto_verification(file_path)
