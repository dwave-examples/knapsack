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

example_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSmallProblem(unittest.TestCase):
    """Test the problem defined by small.csv"""

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

        energy = int(float(self.output.split('\n')[0].split()[-1].strip()))
        item_indices = self.output.split('\n')[1].split(':')[1]
        self.assertEqual(eval(item_indices), [4, 5, 6])
        self.assertEqual(energy, -205)


if __name__ == '__main__':
    unittest.main()
