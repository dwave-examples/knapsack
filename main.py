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
import sys
from knapsack import Knapsack
from dwave.system import LeapHybridSampler

# check that the user has provided data file name, and maximum weight
# which the knapsack can hold
if len(sys.argv) != 3:
    print("Usage: knapsack.py: <data file> <maximum weight>")
    exit(1)

data_file_name = sys.argv[1]
try:
    with open(data_file_name, "r") as myfile:
        input_data = myfile.readlines()
except IOError:
    print("knapsack.py: data file <" + data_file_name + "> missing")
    exit(1)

try:
    Weight_Capacity = float(sys.argv[2])
except ValueError:
    print("Usage: knapsack.py: <data file> <maximum weight>")
    exit(1)

# parse input data
df = pd.read_csv(data_file_name, header=None)
df.columns = ['name', 'cost', 'weight']

# create the Knapsack object
K = Knapsack(df['name'], df['cost'], df['weight'], Weight_Capacity)

# Obtain the knapsack BQM
bqm = K.get_bqm()

sampler = LeapHybridSampler(profile="hss")
sampleset = sampler.sample(bqm, time_limit=10)  # doctest: +SKIP
print("Found solution {} at energy {}.".format(
   K.get_names(sampleset.record.sample[0]), sampleset.first.energy))
