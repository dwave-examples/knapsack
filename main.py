# Copyright 2020 D-Wave Systems, Inc.
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
from math import log, ceil
import dimod

# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)


def get_label(lbl, i):
    return lbl + str(i).zfill(2)


def knapsack_bqm(costs, weights, weight_capacity):

    costs = costs

    # Initialize BQM - use large-capacity BQM so that the problem can be
    # scaled by the user.
    bqm = dimod.AdjVectorBQM(dimod.Vartype.BINARY)

    # Lagrangian multiplier
    # First guess as suggested in Lucas's paper
    lagrange = max(costs)

    # Number of objects
    x_size = len(costs)

    # Lucas's algorithm introduces additional slack variables to handle
    # the inequality. max_y_index indicates the maximum index in the y
    # sum; hence the number of slack variables.
    max_y_index = ceil(log(weight_capacity))

    # Slack variable list for Lucas's algorithm. The last variable has
    # a special value because it terminates the sequence.
    y = [2**n for n in range(max_y_index - 1)]
    y.append(weight_capacity + 1 - 2**(max_y_index - 1))

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        bqm.set_linear(get_label('x', k), lagrange * (weights[k]**2) - costs[k])

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = (get_label('x', i), get_label('x', j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # Hamiltonian y-y terms
    for k in range(max_y_index):
        bqm.set_linear(get_label('y', k), lagrange * (y[k]**2))

    # Hamiltonian yi-yj terms
    for i in range(max_y_index):
        for j in range(i + 1, max_y_index):
            key = (get_label('y', i), get_label('y', j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(max_y_index):
            key = (get_label('x', i), get_label('y', j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]

    return bqm


data_file_name = sys.argv[1] if len(sys.argv) > 1 else "data.txt"
weight_capacity = float(sys.argv[2]) if len(sys.argv) > 2 else 70

# parse input data
df = pd.read_csv(data_file_name, header=None)
df.columns = ['cost', 'weight']

bqm = knapsack_bqm(df['cost'], df['weight'], weight_capacity)

sampler = LeapHybridSampler(profile='hss')
sampleset = sampler.sample(bqm)
var_names = sampleset.variables
n_sols = sampleset.record.sample.shape[0]
for i in range(n_sols):
    solution = [df['weight'][j0] for j0, j in enumerate(sampleset.record.sample[i]) if j == 1. and var_names[j0].startswith('x')]
    print("Found solution {} at energy {}.".format(solution, sampleset.record.energy[i]))
