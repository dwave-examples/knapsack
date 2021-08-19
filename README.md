[![Linux/Mac/Windows build status](
  https://circleci.com/gh/dwave-examples/knapsack.svg?style=svg)](
  https://circleci.com/gh/dwave-examples/knapsack)

# Knapsack

The [knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem) is a
well-known optimization problem. It is encountered, for example, in packing
shipping containers. A shipping container has a weight capacity which it can hold.
Given a collection of objects to be shipped, where each object has a value and a
weight, the problem is to select the optimal objects to pack in the shipping
container. This optimization problem can be defined as an objective with a constraint:

* **Objective:** Maximize the sum total of the values of the objects packed in
  the container.
* **Constraint:** The total weight of the selected objects is less than or equal
  to the container's capacity.

This example solves a knapsack problem on a D-Wave solver by reformulating it as
a constrained quadratic model (CQM) and submitting it to a Leap hybrid CQM solver.

## Usage

To run the default demo, enter the command:

```bash
python knapsack.py
```

To view the available options, enter the command:

```bash
python knapsack.py --help
```

Command-line arguments let you select one of several data sets (under the `/data`
folder) and the maximum weight. The data files include objects defined by pairs
of weight and value.  

## Code Overview

The code in `knapsack.py` includes two functions:

* `build_knapsack_cqm()` creates a CQM by setting an objective and constraint as
  follows:

  - Objective: Binary variables are created for each item, and assigned a linear
    bias equal to the negative value of the item's cost. To minimize this objective
    is equivalent to maximizing the total cost of the items.
  - Constraint: A constraint is created as quadratic model that sets the linear
    biases of the previously created binary variables equal to the weight of each
    item and requires the total to be up to the container's capacity.
* `solve_knapsack()` calls the `build_knapsack_cqm()`, submits the generated CQM
  to a Leap hybrid CQM solver, and parses and displays the results.

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
