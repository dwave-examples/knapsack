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
import sys
from dwave.system import LeapHybridCQMSampler
import dimod

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

    cqm = dimod.ConstrainedQuadraticModel()
    obj = dimod.BinaryQuadraticModel(vartype='BINARY')

    x = {i: obj.add_variable(f'x{i}') for i in range(num_items)}
    for i in range(num_items):
        obj.set_linear(x[i], -costs[i])
    cqm.set_objective(obj)

    constraint = [(x[i], weights[i]) for i in range(num_items)] + [(-weight_capacity, )]
    cqm.add_constraint(constraint, sense="<=", label='capacity')

    return cqm

def solve_knapsack(costs, weights, weight_capacity, sampler=None):
    """Construct a quadratic model and solve the knapsack problem.

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
        sampler = LeapHybridCQMSampler(solver="hybrid_constrained_quadratic_model_version1_test")

    sampleset = sampler.sample_cqm(cqm, label='Example - Knapsack')
    # .first() method returns lowest energy but that solution might be infeasible
    best = next(itertools.filterfalse(lambda d: not getattr(d,'is_feasible'),
                list(sampleset.data())))
    sample = best.sample
    energy = best.energy

    # Build solution from returned binary variables, where 'x'i==1 includes the item
    selected_item_indices = []
    for varname, value in sample.items():
        if value:
            selected_item_indices.append(int(varname[1:]))

    return sorted(selected_item_indices), energy

files = os.listdir("data")

@click.command()
@click.option('--data_file_name', default='data/large.csv',
              help='Name of data file to run on. One of:' + str(files).replace(",", "\n"))
@click.option('--weight_capacity', default=70,
              help='Maximum weight for the container.')
def main(data_file_name, weight_capacity):

    # parse input data
    df = pd.read_csv(data_file_name, names=['cost', 'weight'])

    selected_item_indices, energy = solve_knapsack(costs=df['cost'],
                                                   weights=df['weight'],                     weight_capacity=weight_capacity,
                                                   sampler=None)
    selected_weights = list(df.loc[selected_item_indices,'weight'])
    selected_costs = list(df.loc[selected_item_indices,'cost'])

    print("Found solution at energy {}".format(energy))
    print("Selected item numbers (0-indexed):", selected_item_indices)
    print("Selected item weights: {}, total = {}".format(selected_weights, sum(selected_weights)))
    print("Selected item costs: {}, total = {}".format(selected_costs, sum(selected_costs)))

if __name__ == '__main__':
    main()
