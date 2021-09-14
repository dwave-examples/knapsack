[![Linux/Mac/Windows build status](
  https://circleci.com/gh/dwave-examples/knapsack.svg?style=svg)](
  https://circleci.com/gh/dwave-examples/knapsack)

# Knapsack

The [knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem) is a
well-known optimization problem. It is encountered, for example, in packing
shipping containers. A shipping container has a weight capacity which it can hold.
Given a collection of items to be shipped, where each item has a value and a
weight, the problem is to select the optimal items to pack in the shipping
container. This optimization problem can be defined as an objective with a constraint:

* **Objective:** Maximize freight value (sum of values of the selected items).
* **Constraint:** Total freight weight (sum of weights of the selected items) must
  be less than or equal to the container's capacity.

This example solves such a knapsack problem by reformulating it as
a constrained quadratic model (CQM) and submitting it to a Leap hybrid CQM solver.

## Usage

To run the default demo, enter the command:

```bash
python knapsack.py
```

To view available options, enter the command:

```bash
python knapsack.py --help
```

Command-line arguments let you select one of several data sets (under the `/data`
folder) and set the freight capacity. The data files are formulated as rows of
items, each defined as a pair of weight and value.  

## Code Overview

The code in `knapsack.py` includes three main functions:

* `build_knapsack_cqm()` creates a CQM by setting an objective and constraint as
  follows:

  - Objective: Binary variables are created for each item, and assigned a linear
    bias equal to the negative value of the item's value. To minimize this objective,
    by selecting an optimal set of items, is equivalent to maximizing the total
    value of the freight. Solutions set a value of 1 to selected items and 0 to
    unselected items.
  - Constraint: A quadratic model with the previously created binary variables,
    where the linear biases are set equal to the weight of each item, is created
    with the requirement that the total weight must not exceed the container's
    capacity.
* `parse_inputs()` is a utility function that reads data from the example files.
* `parse_solution()` parses and displays the results returned from the solver.

## License

Released under the Apache License 2.0. See [LICENSE](LICENSE) file.
