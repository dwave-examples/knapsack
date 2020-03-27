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
import unittest

example_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestSmoke(unittest.TestCase):
    # test that the example runs without failing
    def test_smoke(self):
        file_path = os.path.join(example_dir, 'main.py')
        data_file_path = os.path.join(example_dir, 'small_data.txt')
        test_case_weight = '50'

        value = subprocess.check_output(["python", file_path, data_file_path, test_case_weight])

        # Check the expected energy
        energy_expected = "-205"
        self.assertTrue(energy_expected in str(value))

        # Extract the list from the solution
        z = str(value).split(" at energy")
        soln = z[0].split("Found solution ")
        soln_expected = [20, 10, 15]
        self.assertEqual(eval(soln[1]), soln_expected)

if __name__ == '__main__':
    unittest.main()
