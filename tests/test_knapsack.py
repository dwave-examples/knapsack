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
import re

example_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSmoke(unittest.TestCase):
    # test that the example runs without failing
    def test_smoke(self):
        file_path = os.path.join(example_dir, 'main.py')
        data_file_path = os.path.join(example_dir, 'data/small.csv')
        test_case_weight = '50'

        value = subprocess.check_output([sys.executable, file_path,
                                         data_file_path, test_case_weight])

        # Check the expected energy
        energy_expected = "-205"
        self.assertTrue(energy_expected in str(value))

        # Extract the list from the solution
        z = str(value).split(" at energy")
        soln = z[0].split("Found solution ")
        soln_expected = [20, 10, 15]
        self.assertEqual(eval(soln[1]), soln_expected)

    def test_knapsack(self):
        """ Verify contents of output """
        
        file_path = os.path.join(example_dir, 'main.py')
        data_file_path = os.path.join(example_dir, 'data/small.csv')
        output = subprocess.check_output([sys.executable, file_path,
                                         data_file_path, "50"])
        output = str(output).upper()
        if os.getenv('DEBUG_OUTPUT'):
            print("Example output :-"+ output)

        with self.subTest(msg="Verify if output contains 'FOUND SOLUTION' \n"):
            self.assertIn("FOUND SOLUTION", output)
        with self.subTest(msg="Verify if output contains correct energy' \n"):
            self.assertIn("ENERGY -205.0", output)
        with self.subTest(msg="Verify if error string contains in output \n"):
            self.assertNotIn("ERROR", output)
        with self.subTest(msg="Verify if warning string contains in output \n"):
            self.assertNotIn("WARNING", output)

    def test_knapsack_full_demo(self):
        """ Verify contents of output """
        
        file_path = os.path.join(example_dir, 'main.py')
        data_file_path = os.path.join(example_dir, 'data/large.csv')

        # Due to heuristic nature of solver/solution if energy doesn't match the expected one retry few times
        runcount = 0
        energy = 0
        upperbound_energy = -515
        lowerbound_energy = -524
        while runcount < 3 and not lowerbound_energy < energy <= upperbound_energy:
            output = subprocess.check_output([sys.executable, file_path, data_file_path])
            output = str(output).upper()

            if os.getenv('DEBUG_OUTPUT'):
                print("Example output :-"+ output)
            
            # Get energy value returned by solution
            regex = r'ENERGY\s*([+-]?\d+(\.\d*)?)'
            energy = float(next(re.finditer(regex, output, re.I)).group(1))
            runcount += 1

        with self.subTest(msg="Verify if output contains 'FOUND SOLUTION' \n"):
            self.assertIn("FOUND SOLUTION", output)
        with self.subTest(msg="Verify energy is between "+ str(upperbound_energy) +" and "+ str(lowerbound_energy) +"'\n"):
            self.assertTrue(lowerbound_energy < energy <= upperbound_energy)
        with self.subTest(msg="Verify if error string contains in output \n"):
            self.assertNotIn("ERROR", output)
        with self.subTest(msg="Verify if warning string contains in output \n"):
            self.assertNotIn("WARNING", output)

if __name__ == '__main__':
    unittest.main()
