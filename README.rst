========
Knapsack
========

This code runs the knapsack problem. The knapsack problem is well-known optimization problem, for example found in packing shipping containers on docks. To solve on a D-Wave system, we reformulate this problem as a quadratic unconstrained binary optimization problem (QUBO).

The knapsack problem presents a collection of objects. Each object has a value, and a weight. The knapsack has a weight capacity which it can hold. The goal is to pack the knapsack in order to:
1) maximize the sum total of the values of the objects put into the knapsack
2) fill up the knapsack so that the total weight is less than or equal to the knapsack's capacity.

Usage
-----

To run a small demo, run the command:

.. code-block:: bash

  python main.py small_data.txt 50

The answer should include three objects, with combined weight of 45 kg, below 
the maximum of 50 kg. Their summed value is 205, which agrees with the
reported energy.

To run the full demo, run the command:

.. code-block:: bash

  python main.py data.txt 70


Code Overview
-------------

knapsack.py contains an implementation of Andrew Lucas's improved formulation[2] based on his original writeup[1]. Lucas's formulation adds slack variables to handle the less-than-or-equal-to constraint.

The x variables determine whether the weights are to be included in the selected set, and the y variables are the slack variables. The code separates out the x-x, x-y, and y-y terms.


References
----------

.. [1] Andrew Lucas, "Ising formulations of many NP problems", `doi: 10.3389/fphy.2014.00005 <https://www.frontiersin.org/articles/10.3389/fphy.2014.00005/full>`_

.. [2] Andrew Lucas, "NP-hard combinatorial problems as Ising spin glasses,"
Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014


License
-------

Released under the Apache License 2.0. See `LICENSE <LICENSE>`_ file.
