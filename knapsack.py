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

# ------ Import necessary packages ------
from math import log, ceil
from collections import defaultdict
import dimod


# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)

class Knapsack(object):

    def __init__(self, names, costs, weights, Weight_Capacity):

        self.names = names
        self.costs = costs

        # Initialize QUBO dict
        self.qubo = defaultdict(float)

        # Lagrangian multiplier
        Lagrange = max(costs)

        # Number of objects
        x_size = len(costs)

        # Lucas's algorithm introduces additional slack variables to handle
        # the inequality. max_y_index indicates the maximum index in the y
        # sum; hence the number of slack variables.
        max_y_index = ceil(log(Weight_Capacity))

        # Slack variable list for Lucas's algorithm. The last variable has
        # a special value because it terminates the sequence.
        y = [2 ** n for n in range(max_y_index - 1)]
        y.append(Weight_Capacity + 1 - 2 ** (max_y_index - 1))

        # Hamiltonian xi-xi terms
        for k in range(x_size):
            key = ('x' + str(k), 'x' + str(k))
            self.qubo[key] = Lagrange * (weights[k] ** 2) - costs[k]

        # Hamiltonian xi-xj terms
        for i in range(x_size):
            for j in range(i + 1, x_size):
                key = ('x' + str(i), 'x' + str(j))
                self.qubo[key] = 2 * Lagrange * weights[i] * weights[j]

        # Hamiltonian y-y terms
        for k in range(max_y_index):
            key = ('y' + str(k), 'y' + str(k))
            self.qubo[key] = Lagrange * (y[k] ** 2)

        # Hamiltonian yi-yj terms
        for i in range(max_y_index):
            for j in range(i + 1, max_y_index):
                key = ('y' + str(i), 'y' + str(j))
                self.qubo[key] = 2 * Lagrange * y[i] * y[j]

        # Hamiltonian x-y terms
        for i in range(x_size):
            for j in range(max_y_index):
                key = ('x' + str(i), 'y' + str(j))
                self.qubo[key] = -2 * Lagrange * weights[i] * y[j]

    def get_bqm(self):
        return dimod.BinaryQuadraticModel.from_qubo(self.qubo)

    def get_names(self, solution):
        return [self.names[i] for i in range(len(self.costs)) if solution[i] == 1.]
