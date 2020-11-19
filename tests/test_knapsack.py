# Copyright 2020 D-Wave Systems Inc.
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
import os
import subprocess
import sys
import unittest
import pandas as pd
import re
import ast

import dimod

# Add the parent path so that the test file can be run as a script in
# addition to using "python -m unittest" from the root directory
example_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(example_dir)
import knapsack


class TestExactSolver(unittest.TestCase):
    """Test problems using the exact solver"""

    def _exact_solver_driver(self, data_file, max_weight, expected_energy, expected_item_indices):
        """Utility routine to perform a test on the exact solver and compare to expected solution"""
        sampler = dimod.ExactSolver()

        df = pd.read_csv(data_file, names=['cost', 'weight'])

        selected_item_indices, energy = knapsack.solve_knapsack(df['cost'], df['weight'], max_weight, sampler=sampler)

        self.assertEqual(energy, expected_energy)
        self.assertEqual(selected_item_indices, expected_item_indices)
        
    def test_small_problem(self):
        """Test the small.csv problem"""
        data_file_name = os.path.join(example_dir, 'data/small.csv')
        self._exact_solver_driver(data_file_name, 50, -205, [4, 5, 6])

    def test_very_small_problem(self):
        """Test the very_small.csv problem"""
        data_file_name = os.path.join(example_dir, 'data/very_small.csv')
        self._exact_solver_driver(data_file_name, 10, -10, [0])


class IntegrationTest(unittest.TestCase):
    """Test the main program run as a script using the small.csv data"""

    @classmethod
    def setUpClass(cls):
        """Utility method that runs the problem and stores the output"""
        
        file_path = os.path.join(example_dir, 'knapsack.py')
        data_file_path = os.path.join(example_dir, 'data/small.csv')
        test_case_weight = '50'

        cls.output = subprocess.check_output([sys.executable, file_path,
                                              data_file_path, test_case_weight])
        cls.output = cls.output.decode('utf-8') # Bytes to str

    def test_smoke(self):
        """Verify that the executable script runs and reports some solution"""

        self.assertIn("found solution", self.output.lower())

    def test_solution(self):
        """Verify that the expected solution is obtained"""

        energy = int(float(re.search(r'energy\s+([+-]?\d+(\.\d*)?)', self.output, re.I).group(1)))
        item_indices = re.search(r'item numbers.*:\s*(\[[^]]*\])', self.output, re.I).group(1)
        # Note: item indices in the output are sorted
        self.assertEqual(ast.literal_eval(item_indices), [4, 5, 6])
        self.assertEqual(energy, -205)


if __name__ == '__main__':
    unittest.main()
