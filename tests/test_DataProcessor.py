import unittest
import json
import os
from e_pdf_form_reader.DataProcessor import DataProcessor

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.test_data = {'key': 'value'}
        self.output_file = 'test_output.json'

    def tearDown(self):
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_save_to_json(self):
        DataProcessor.save_to_json(self.test_data, self.output_file)
        self.assertTrue(os.path.exists(self.output_file))

    def test_refile_results(self):
        # Sample input data
        results = [
            {'kind': 'rowdict', 'load': {'A': {'field1': 'value1', 'field2': 'value2'}}, 'name': 'name1'},
            {'kind': 'dict', 'load': {'field3': 'value3', 'field4': 'value4'}},
            {'kind': 'text', 'load': 'Sample Text'},
            {'kind': 'other', 'load': 'Other Data', 'name': 'name2'}
        ]
        
        # Expected output
        expected_output = {
            'SCR.RD0000.A.field1': 'value1',
            'SCR.RD0000.A.field2': 'value2',
            'field3': 'value3',
            'field4': 'value4',
            'TXT.Sample Text': 'Sample Text',
            'name2': 'Other Data'
        }
        
        # Call the refile_results function
        actual_output = DataProcessor.refile_results(results)
        
        # Assertion
        self.assertEqual(expected_output, actual_output)


if __name__ == '__main__':
    unittest.main()
