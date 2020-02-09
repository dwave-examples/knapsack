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
import pandas as pd
from knapsack import Knapsack
from dwave.system import LeapHybridSampler
import click
import numpy as np

# Handle command-line arguments
@click.command()
@click.argument('data_file_name')
@click.argument('max_weight', default=1.)
def main(data_file_name, max_weight):

    # check that the user has provided data file name, and maximum weight
    # which the knapsack can hold
    try:
        with open(data_file_name, "r") as myfile:
            input_data = myfile.readlines()
    except IndexError:
        print("Usage: knapsack.py: <data file> <maximum weight>")
        exit(1)
    except IOError:
        print("knapsack.py: data file <" + data_file_name + "> missing")
        exit(1)

    try:
        W = float(max_weight)
    except IndexError:
        print("Usage: knapsack.py: <data file> <maximum weight>")
        exit(1)

    if W <= 0.:
        print("Usage: knapsack.py: <maximum weight> must be positive")
        exit(1)

    # parse input data
    df = pd.read_csv(data_file_name, header=None)
    df.columns = ['name', 'cost', 'wt']

    # create the Knapsack object
    K = Knapsack(df['name'], df['cost'], df['wt'], W)

    # Obtain the knapsack BQM
    bqm = K.get_bqm()

    sampler = LeapHybridSampler(profile="hss")
    sampleset = sampler.sample(bqm, time_limit=10)  # doctest: +SKIP
    print("Found solution {} at energy {}.".format(
       K.get_names(sampleset.record.sample[0]), sampleset.first.energy))


if __name__ == '__main__':
    main()
