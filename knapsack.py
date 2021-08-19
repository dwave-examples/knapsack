# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import itertools
import click
import pandas as pd
from dwave.system import LeapHybridCQMSampler
from dimod import ConstrainedQuadraticModel, BinaryQuadraticModel

def build_knapsack_cqm(costs, weights, weight_capacity):
    """Construct a CQM for the knapsack problem.

    Args:
        costs (array-like):
            Array of costs associated with the items.
        weights (array-like):
            Array of weights associated with the items.
        weight_capacity (int):
            Maximum allowable weight.

    Returns:
        Constrained quadratic model instance.
    """
    num_items = len(costs)
    print("Building a CQM for {} items.".format(str(num_items)))

    cqm = ConstrainedQuadraticModel()
    obj = BinaryQuadraticModel(vartype='BINARY')

    # Objective is to maximize the total costs
    for i in range(num_items):
        obj.add_variable(i)
        obj.set_linear(i, -costs[i])
    cqm.set_objective(obj)

    # Constraint is that the sum of all items' weights be up to maximum capacity
    constraint = [(i, weights[i]) for i in range(num_items)]
    cqm.add_constraint(constraint, sense="<=", rhs=weight_capacity, label='capacity')

    return cqm

def solve_knapsack(costs, weights, weight_capacity, sampler=None):
    """Construct a CQM for, and solve, the knapsack problem.

    Args:
        costs (array-like):
            Array of costs associated with the items.
        weights (array-like):
            Array of weights associated with the items.
        weight_capacity (int):
            Maximum allowable weight.
        sampler (BQM sampler instance or None):
            A sampler instance or None, in which case LeapHybridCQMSampler is used
            by default for CQMs and LeapHybridSampler for BQMs.

    Returns:
        Tuple:
            List of indices of selected items.
            Solution energy.
    """
    cqm = build_knapsack_cqm(costs, weights, weight_capacity)

    if sampler is None:
        # TODO: remove filtering on block solver
        sampler = LeapHybridCQMSampler(solver="hybrid_constrained_quadratic_model_version1_test")

    print("Submitting CQM to solver {}.".format(sampler.solver.name))
    sampleset = sampler.sample_cqm(cqm, label='Example - Knapsack')
    # .first() method returns lowest energy but that solution might be infeasible
    best = next(itertools.filterfalse(lambda d: not getattr(d,'is_feasible'),
                list(sampleset.data())))

    selected_item_indices = [key for key, val in best.sample.items() if val==1.0]

    return sorted(selected_item_indices), best.energy

# Format the help display ("\b" enables newlines in click() help text)
datafiles = os.listdir("data")
datafile_help = """
Name of data file (under the data\ folder) to run on. One of:\n
File Name \t\t Total weight\n
\b
"""
for file in datafiles:
    df = pd.read_csv("data/" + file, names=['cost', 'weight'])
    datafile_help += str(file) + "\t\t" + str(sum(df['weight'])) + "\n"
datafile_help += "\nDefault is to run on data/large.csv."

@click.command()
@click.option('--data_file_name', default='data/large.csv',
              help=datafile_help)
@click.option('--weight_capacity', default=None,
              help="Maximum weight for the container. By default sets 80% of the total.")
def main(data_file_name, weight_capacity):
    """Solve a knapsack problem using a CQM solver."""

    df = pd.read_csv(data_file_name, names=['cost', 'weight'])

    if not weight_capacity:
        weight_capacity = int(0.8 * sum(df['weight']))
        print("Setting weight capacity to 80% of total: {}".format(str(weight_capacity)))

    selected_item_indices, energy = solve_knapsack(costs=df['cost'],
                                                   weights=df['weight'],                     weight_capacity=weight_capacity,
                                                   sampler=None)
    selected_weights = list(df.loc[selected_item_indices,'weight'])
    selected_costs = list(df.loc[selected_item_indices,'cost'])

    print("\nFound best solution at energy {}".format(energy))
    print("\nSelected item numbers (0-indexed):", selected_item_indices)
    print("\nSelected item weights: {}, total = {}".format(selected_weights, sum(selected_weights)))
    print("\nSelected item costs: {}, total = {}".format(selected_costs, sum(selected_costs)))

if __name__ == '__main__':
    main()
