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
import click
import pandas as pd
import sys
from dwave.system import LeapHybridSampler, LeapHybridCQMSampler
from math import log2, floor
import dimod

# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)
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

def build_knapsack_bqm(costs, weights, weight_capacity):
    """Construct a BQM for the knapsack problem.

    Args:
        costs (array-like):
            Array of costs associated with the items.
        weights (array-like):
            Array of weights associated with the items.
        weight_capacity (int):
            Maximum allowable weight.

    Returns:
        Binary quadratic model instance.
    """

    bqm = dimod.BQM(dimod.Vartype.BINARY)


    lagrange = max(costs)   # Lagrangian multiplier as suggested in Lucas's paper
    x_size = len(costs)     # Number of objects

    # Lucas's algorithm introduces M+1 binary slack variables to
    # handle the inequality, with the sum represented as a set of powers of 2.
    M = floor(log2(weight_capacity))
    num_slack_variables = M + 1

    # The last slack variable in the list has
    # a special value because it terminates the sequence.
    y = [2**n for n in range(M)]
    y.append(weight_capacity + 1 - 2**M)

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        bqm.set_linear('x' + str(k), lagrange * (weights[k]**2) - costs[k])

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # Hamiltonian y-y terms
    for k in range(num_slack_variables):
        bqm.set_linear('y' + str(k), lagrange * (y[k]**2))

    # Hamiltonian yi-yj terms
    for i in range(num_slack_variables):
        for j in range(i + 1, num_slack_variables):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(num_slack_variables):
            key = ('x' + str(i), 'y' + str(j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]

    return bqm

def solve_knapsack(costs, weights, weight_capacity, bqm, sampler=None):
    """Construct a quadratic model and solve the knapsack problem.

    Args:
        costs (array-like):
            Array of costs associated with the items.
        weights (array-like):
            Array of weights associated with the items.
        weight_capacity (int):
            Maximum allowable weight.
        model (str):
            Selects whether to construct a constrained quadratic model (CQM) or
            binary quadratic model (BQM), and then solve using the appropriate
            sampler.
        sampler (BQM sampler instance or None):
            A sampler instance or None, in which case LeapHybridCQMSampler is used
            by default for CQMs and LeapHybridSampler for BQMs.

    Returns:
        Tuple:
            List of indices of selected items.
            Solution energy.
    """
    build_knapsack = {'bqm': build_knapsack_bqm, 'cqm': build_knapsack_cqm}
    default_sampler = {'bqm': LeapHybridSampler(solver="hybrid_binary_quadratic_model_version2p_test"),
                       'cqm': LeapHybridCQMSampler(solver="hybrid_constrained_quadratic_model_version1_test")}

    model = 'cqm'
    if bqm:
        model = 'bqm'

    qm = build_knapsack[model](costs, weights, weight_capacity)

    if sampler is None:
        sampler = default_sampler[model]

    # if bqm:
    #     qm = build_knapsack_bqm(costs, weights, weight_capacity)
    # else:
    #     qm = build_knapsack_cqm(costs, weights, weight_capacity)
    #
    # if sampler is None:
    #     if bqm:
    #         # TODO: remove solver name used to avoid bulk
    #         sampler = LeapHybridSampler(solver="hybrid_binary_quadratic_model_version2p_test")
    #     else:
    #         # TODO: remove solver name used to avoid bulk
    #         sampler = LeapHybridCQMSampler(solver="hybrid_constrained_quadratic_model_version1_test")
    #
    if bqm:
        sampleset = sampler.sample(qm, label='Example - Knapsack')
    else:
        sampleset = sampler.sample_cqm(qm, label='Example - Knapsack')

    sample = sampleset.first.sample
    energy = sampleset.first.energy

    selected_item_indices = []
        # Build solution from returned binary variables:
    for varname, value in sample.items():
        # For each "x" variable, check whether its value is set, which
        # indicates that the corresponding item is included in the
        # knapsack
        if value and varname.startswith('x'):
            # The index into the weight array is retrieved from the
            # variable name
            selected_item_indices.append(int(varname[1:]))
            
    return sorted(selected_item_indices), energy

files = os.listdir("data")

@click.command()
@click.option('--bqm', is_flag=True,
              help='Set to build and solve a binary quadratic model. By default \
builds a constrained quadratic model.')
@click.option('--data_file_name', default='data/large.csv',
              help='Name of data file to run on. One of:' + str(files))
@click.option('--weight_capacity', default=70,
              help='Maximum weight for the container.')
def main(bqm, data_file_name, weight_capacity):

    #data_file_name = sys.argv[1] if len(sys.argv) > 1 else "data/large.csv"
    #weight_capacity = float(sys.argv[2]) if len(sys.argv) > 2 else 70

    # parse input data
    df = pd.read_csv(data_file_name, names=['cost', 'weight'])

    selected_item_indices, energy = solve_knapsack(costs=df['cost'],
                                                   weights=df['weight'],                     weight_capacity=weight_capacity,
                                                   bqm=bqm,
                                                   sampler=None)
    selected_weights = list(df.loc[selected_item_indices,'weight'])
    selected_costs = list(df.loc[selected_item_indices,'cost'])

    print("Found solution at energy {}".format(energy))
    print("Selected item numbers (0-indexed):", selected_item_indices)
    print("Selected item weights: {}, total = {}".format(selected_weights, sum(selected_weights)))
    print("Selected item costs: {}, total = {}".format(selected_costs, sum(selected_costs)))

if __name__ == '__main__':
    main()
