========
Knapsack
========

This code runs the knapsack problem.
Consider a set of objects, for example:

95_kg,77,95
70_kg,44,70
85_kg,15,85
31_kg,67,31
100_kg,75,100
...

The first column is the name of the object; the second column is a value that
is associated with the object; and the third column is the weight of the object.
Consider a knapsack, which has a maximum weight W. The goal of the knapsack
problem is to pack objects into the knapsack to do the following:
- maximize the sum total of the values of the objects put into the knapsack
- fill up the knapsack so that the total weight is less than or equal to W

The knapsack problem is well-known optimization problem. To solve on a D-Wave system, we can reformulate this problem as a quadratic unconstrained binary optimization problem (QUBO).

Usage
-----

To run a small demo, consider the following objects:

12_kg,35,12
27_kg,85,27
10_kg,30,10
17_kg,50,17
20_kg,70,20
10_kg,80,10
15_kg,55,15

Run the command:

.. code-block:: bash

  python main.py small_data.txt 50

The answer should include the last three object. Their combined weight is
45 kg, below the maximum of 50 kg. Their value is 205, which agrees with the
reported energy.

To run the demo, run:

.. code-block:: bash

  python main.py data.txt 150


Code Overview
-------------

knapsack.py contains an implementation of Andrew Lucas's improved formulation[2] based on his original writeup[1].


References
----------

.. [1] Andrew Lucas, "Ising formulations of many NP problems", `doi: 10.3389/fphy.2014.00005 <https://www.frontiersin.org/articles/10.3389/fphy.2014.00005/full>`_

.. [2] Andrew Lucas, "NP-hard combinatorial problems as Ising spin glasses,"
Workshop on Classical and Quantum Optimization; ETH Zuerich - August 20, 2014


License
-------

Released under the Apache License 2.0. See `LICENSE <LICENSE>`_ file.
