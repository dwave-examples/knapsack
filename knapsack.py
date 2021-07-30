# Copyright 2020 D-Wave Systems Inc.
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

import pandas as pd
import sys
from dwave.system import LeapHybridSampler
import dimod

# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)


def build_knapsack_bqm(costs, weights, weight_capacity):
    """Construct BQM for the knapsack problem

    Args:
        costs (array-like):
            Array of costs associated with the items
        weights (array-like):
            Array of weights associated with the items
        weight_capacity (int):
            Maximum allowable weight

    Returns:
        Binary quadratic model instance
    """

    # Initialize BQM - use large-capacity BQM so that the problem can be
    # scaled by the user.
    bqm = dimod.BinaryQuadraticModel(dimod.Vartype.BINARY)


    # Lagrangian multiplier
    # First guess as suggested in Lucas's paper
    lagrange = max(costs)

    # Number of objects
    x_size = len(costs)

    # set the objective by specifying the linear cofficient of each
    # variables as the minus of cost
    for k in range(x_size):
        bqm.set_linear('x' + str(k), - costs[k])

    # add the capacity constraint as a linear inequality constraint
    bqm.add_linear_inequality_constraint(
        [('x' + str(k), weights[k]) for k in range(x_size)],
        constant=-weight_capacity,
        lagrange_multiplier=lagrange,
        label='weight_capacity'
    )
    return bqm

def solve_knapsack(costs, weights, weight_capacity, sampler=None):
    """Construct BQM and solve the knapsack problem

    Args:
        costs (array-like):
            Array of costs associated with the items
        weights (array-like):
            Array of weights associated with the items
        weight_capacity (int):
            Maximum allowable weight
        sampler (BQM sampler instance or None):
            A BQM sampler instance or None, in which case
            LeapHybridSampler is used by default

    Returns:
        Tuple:
            List of indices of selected items
            Solution energy
    """
    bqm = build_knapsack_bqm(costs, weights, weight_capacity)

    if sampler is None:
        sampler = LeapHybridSampler()

    sampleset = sampler.sample(bqm, label='Example - Knapsack')
    sample = sampleset.first.sample
    energy = sampleset.first.energy

    # Build solution from returned binary variables:
    selected_item_indices = []
    for varname, value in sample.items():
        # For each "x" variable, check whether its value is set, which
        # indicates that the corresponding item is included in the
        # knapsack
        if value and varname.startswith('x'):
            # The index into the weight array is retrieved from the
            # variable name
            selected_item_indices.append(int(varname[1:]))

    return sorted(selected_item_indices), energy


if __name__ == '__main__':

    data_file_name = sys.argv[1] if len(sys.argv) > 1 else "data/large.csv"
    weight_capacity = float(sys.argv[2]) if len(sys.argv) > 2 else 70

    # parse input data
    df = pd.read_csv(data_file_name, names=['cost', 'weight'])

    selected_item_indices, energy = solve_knapsack(df['cost'], df['weight'], weight_capacity)
    selected_weights = list(df.loc[selected_item_indices,'weight'])
    selected_costs = list(df.loc[selected_item_indices,'cost'])

    print("Found solution at energy {}".format(energy))
    print("Selected item numbers (0-indexed):", selected_item_indices)
    print("Selected item weights: {}, total = {}".format(selected_weights, sum(selected_weights)))
    print("Selected item costs: {}, total = {}".format(selected_costs, sum(selected_costs)))
