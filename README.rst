========
Knapsack
========

Consider a problem found in packing shipping containers on docks. There is a collection of objects; each object has a value, and a weight. The shipping container has a weight capacity which it can hold. The goal is to pack the shipping container in order to:
1) maximize the sum total of the values of the objects put into the container.
2) fill up the container so that the total weight is less than or equal to the container's capacity.

This well-known optimization problem is known as the knapsack problem.
To solve this problem on a D-Wave system, we reformulate it as a quadratic unconstrained binary optimization problem (QUBO).


Usage
-----

To run a small demo, run the command:

.. code-block:: bash

  python main.py small_data.txt 50

The command-line arguments specify the Python program, a small data set, and the maximum weight (in kilograms). The small data set file includes objects, provided as pairs (weight, value). 
The answer should include three objects, with combined weight of 45 kg, below 
the maximum of 50 kg. Their summed value is 205, which agrees with the
reported energy.

To run the full demo, run the command:

.. code-block:: bash

  python main.py


Code Overview
-------------

main.py contains an implementation of Andrew Lucas's improved formulation[2] based on his original writeup[1]. Lucas's formulation adds slack variables to handle the less-than-or-equal-to constraint.

The x variables in main.py determine whether the weights are to be included in the selected set, and the y variables in main.py are the slack variables. 
The code separates out the x-x, x-y, and y-y terms.

The Hamiltonian includes the constraints that the sum of the y variables must
be 1; the weight of the knapsack can take only one value. There is also the 
constraint that the sum of all the weights multiplied by the x variables must
be less than or equal to the knapsack's weight capacity. The energy term multiplies the costs by the x variables, in order to represent the overall weight placed into the knapsack. The slack variables turn the inequality into an equality.

References
----------

.. [1] Andrew Lucas, "Ising formulations of many NP problems", `doi: 10.3389/fphy.2014.00005 <https://www.frontiersin.org/articles/10.3389/fphy.2014.00005/full>`_

.. [2] Andrew Lucas, "NP-hard combinatorial problems as Ising spin glasses,"
Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014


License
-------

Released under the Apache License 2.0. See `LICENSE <LICENSE>`_ file.
