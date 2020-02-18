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


def knapsack_bqm(costs, weights, weight_capacity):

    costs = costs

    # Initialize BQM
    bqm = dimod.AdjVectorBQM(dimod.Vartype.BINARY)

    # Lagrangian multiplier
    lagrange = max(costs)

    # Number of objects
    x_size = len(costs)

    # Lucas's algorithm introduces additional slack variables to handle
    # the inequality. max_y_index indicates the maximum index in the y
    # sum; hence the number of slack variables.
    max_y_index = ceil(log(weight_capacity))

    # Slack variable list for Lucas's algorithm. The last variable has
    # a special value because it terminates the sequence.
    y = [2 ** n for n in range(max_y_index - 1)]
    y.append(weight_capacity + 1 - 2 ** (max_y_index - 1))

    # Hamiltonian xi-xi terms
    for k in range(x_size):
        bqm.set_linear('x' + str(k), lagrange * (weights[k] ** 2) - costs[k])

    # Hamiltonian xi-xj terms
    for i in range(x_size):
        for j in range(i + 1, x_size):
            key = ('x' + str(i), 'x' + str(j))
            bqm.quadratic[key] = 2 * lagrange * weights[i] * weights[j]

    # Hamiltonian y-y terms
    for k in range(max_y_index):
        bqm.set_linear('y' + str(k), lagrange * (y[k] ** 2))

    # Hamiltonian yi-yj terms
    for i in range(max_y_index):
        for j in range(i + 1, max_y_index):
            key = ('y' + str(i), 'y' + str(j))
            bqm.quadratic[key] = 2 * lagrange * y[i] * y[j]

    # Hamiltonian x-y terms
    for i in range(x_size):
        for j in range(max_y_index):
            key = ('x' + str(i), 'y' + str(j))
            bqm.quadratic[key] = -2 * lagrange * weights[i] * y[j]

    return bqm


# check that the user has provided data file name, and maximum weight
# which the knapsack can hold
if len(sys.argv) != 3:
    raise TypeError("Incorrect number of arguments")

data_file_name = sys.argv[1]
try:
    with open(data_file_name, "r") as myfile:
        input_data = myfile.readlines()
except IOError:
    print("knapsack.py: data file <" + data_file_name + "> missing")
    exit(1)

try:
    weight_capacity = float(sys.argv[2])
except ValueError:
    print("Usage: knapsack.py: <data file> <maximum weight>")
    exit(1)

# parse input data
df = pd.read_csv(data_file_name, header=None)
df.columns = ['cost', 'weight']

bqm = knapsack_bqm(df['cost'], df['weight'], weight_capacity)

sampler = LeapHybridSampler(profile="alpha")
sampleset = sampler.sample(bqm, time_limit=10)  # doctest: +SKIP
solution = [df['weight'][i] for i in range(len(df['weight'])) if sampleset.record.sample[0][i] == 1.]

print("Found solution {} at energy {}.".format(solution, sampleset.first.energy))
