from math import log
from collections import defaultdict
import dimod


# From Andrew Lucas, NP-hard combinatorial problems as Ising spin glasses
# Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014
# based on Lucas, Frontiers in Physics _2, 5 (2014)

class Knapsack(object):

    def __init__(self, names, costs, weights, W):

        self.names = names
        self.costs = costs

        # Initialize QUBO matrix
        self.qubo = defaultdict(float)

        # Lagrangian multiplier
        A = max(costs)

        # Lucas parameters
        logw = int(log(W)) + 1
        m = logw - 1

        x_size = len(costs)
        y = [2 ** n for n in range(m)]
        y.append(W + 1 - (2 ** m))

        # xi-xi terms
        self.qubo = {('x' + str(k), 'x' + str(k)): A * (weights[k] ** 2) - costs[k] for k in range(x_size)}
        # xi-xj terms
        self.qubo_xi_xj = {('x' + str(i), 'x' + str(j)): 2 * A * weights[i] * weights[j] for i in range(x_size) for j in range(i + 1, x_size)}
        # merge QUBO
        self.qubo.update(self.qubo_xi_xj)

        # y-y terms
        for k in range(logw):
            self.qubo[('y' + str(k), 'y' + str(k))] = A * (y[k] ** 2)
        for i in range(logw):
            for j in range(i + 1, logw):
                self.qubo[('y' + str(i), 'y' + str(j))] = 2 * A * y[i] * y[j]

        # x-y terms
        for i in range(x_size):
            for j in range(logw):
                self.qubo[('x' + str(i), 'y' + str(j))] = -2 * A * weights[i] * y[j]

    def get_bqm(self):
        return dimod.BinaryQuadraticModel.from_qubo(self.qubo)

    def get_names(self, solution):
        return [self.names[i] for i in range(len(self.costs)) if solution[i] == 1.]
