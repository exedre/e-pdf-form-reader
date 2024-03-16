import os
import unittest
from Config import Config

class TestConfig(unittest.TestCase):

    def setUp(self):
        # Prepara una configurazione di test
        self.config_data = {
            'field1': {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'kind': 'single'},
            'field2': {'up-left': '10,10', 'down-right': '110,110', 'page': '2', 'cast': 'float', 'kind': 'single'},
            'field3': {'up-left': '20,20', 'down-right': '120,120', 'page': '3', 'cast': 'date', 'kind': 'single'},
        }
        module_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(module_dir, "test_config.ini")
        self.config = Config(self.config_file)
        self.other_config_data = self.config.config_data
        self.config.config_data = self.config_data
        
    def test_config_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Config("non_existent_config.ini")
            
    def test_load_config(self):
        expected_config_data = {'Section1': {'key1': 'value1', 'key2': 'value2'}, 'Section2': {'key3': 'value3'}}
        self.assertEqual(self.other_config_data, expected_config_data)

    def test_parse_field_type(self):
        # Test con diversi tipi di campi
        test_cases = [
            ("field1", "str"),
            ("field2(int)", "int"),
            ("field3(bool)", "bool"),
            ("field4(float)", "float"),
            ("field5(date)", "date"),
            ("field6(date %Y-%m-%d)", "date %Y-%m-%d"),
            ("field7", "str"),
            ("field8(int)", "int"),
            ("field9(bool)", "bool"),
            ("field10(float)", "float"),
            ("field11(date)", "date"),
            ("field12(date %Y-%m-%d)", "date %Y-%m-%d"),
            ("field13", "str"),
            ("field14(int)", "int"),
            ("field15(bool)", "bool"),
            ("field16(float)", "float"),
            ("field17(date)", "date"),
            ("field18(date %Y-%m-%d)", "date %Y-%m-%d"),
        ]

        for name, expected_type in test_cases:
            with self.subTest(name=name):
                field_name, field_type = self.config.parse_field_type(name)
                self.assertEqual(field_type, expected_type)

    def test_check_mandatory_keys(self):
        data = {'key1': 'value1', 'key2': 'value2'}
        missing_keys = self.config.check_mandatory_keys(data, 'key1', 'key3')
        self.assertEqual(missing_keys, ['key3'])

    def test_create_single_field(self):
        field_data1 = self.config.create_single_field('field1', self.config_data['field1'])
        self.assertEqual(len(field_data1), 1)
        self.assertEqual(field_data1[0]['bbox'], (0.0, 0.0, 100.0, 100.0))
        self.assertEqual(field_data1[0]['kind'], 'str')
        self.assertEqual(field_data1[0]['page'], 1)
        self.assertEqual(field_data1[0]['name'], 'field1')

        field_data2 = self.config.create_single_field('field2', self.config_data['field2'])
        self.assertEqual(field_data2[0]['kind'], 'float')

        field_data3 = self.config.create_single_field('field3', self.config_data['field3'])
        self.assertEqual(field_data3[0]['kind'], 'date')

    def test_expand_row_range(self):
        rows = ('row1', 'row2', 'row3')
        expanded_rows = self.config.expand_row_range(rows)
        self.assertEqual(expanded_rows, ['row1', 'row2', 'row3'])

        rows = ('row1', 'row2-5', 'row6')
        expanded_rows = self.config.expand_row_range(rows)
        self.assertEqual(expanded_rows, ['row1', 'row2', 'row3', 'row4', 'row5', 'row6'])

    def test_create_multi_row_fields(self):
        # Test con righe specifiche
        data1 = {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'rows': 'row1,row2,row3'}
        fields1 = self.config.create_multi_row_fields('section1', data1)
        self.assertEqual(len(fields1), 3)
        self.assertEqual(fields1[0]['name'], 'row1')
        self.assertEqual(fields1[1]['name'], 'row2')
        self.assertEqual(fields1[2]['name'], 'row3')

        # Test con intervallo di righe
        data2 = {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'rows': 'row1-3'}
        fields2 = self.config.create_multi_row_fields('section2', data2)
        self.assertEqual(len(fields2), 3)
        self.assertEqual(fields2[0]['name'], 'row1')
        self.assertEqual(fields2[1]['name'], 'row2')
        self.assertEqual(fields2[2]['name'], 'row3')

        # Test con tipo di campo diverso
        data3 = {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'rows': 'row1,row2,row3', 'cast': 'float'}
        fields3 = self.config.create_multi_row_fields('section3', data3)
        self.assertEqual(len(fields3), 3)
        self.assertEqual(fields3[0]['kind'], 'float')
        self.assertEqual(fields3[1]['kind'], 'float')
        self.assertEqual(fields3[2]['kind'], 'float')

        # Test con prefisso di gruppo
        data4 = {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'rows': 'row1,row2,row3', 'group': 'group1'}
        fields4 = self.config.create_multi_row_fields('section4', data4)
        self.assertEqual(len(fields4), 3)
        self.assertEqual(fields4[0]['name'], 'group1.row1')
        self.assertEqual(fields4[1]['name'], 'group1.row2')
        self.assertEqual(fields4[2]['name'], 'group1.row3')
        
    def test_create_field_model(self):
        # Esegui il metodo create_field_model
        self.setUp()
        self.config.create_field_model()
        # Verifica che field_model sia stato popolato correttamente
        self.assertEqual(len(self.config.field_model), 3)
        self.assertEqual(self.config.field_model[0]['fields'][0]['name'], 'field1')
        self.assertEqual(self.config.field_model[1]['fields'][0]['name'], 'field2')
        self.assertEqual(self.config.field_model[2]['fields'][0]['name'], 'field3')


    def test_create_table_fields(self):
        config_data = {
            'table1': {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'rows': 'row1:str,row2:int,row3:float', 'columns': 'col1:str,col2:int,col3:float'},
            'table2': {'up-left': '10,10', 'down-right': '110,110', 'page': '2', 'rows': 'row1:str,row2:int,row3:float', 'columns': 'col1:str,col2:int,col3:float'},
        }

        config = Config()
        config.config_data = config_data

        table1_expected_fields = [
            {'bbox': (0.0, 0.0, 33.333333333333336, 33.333333333333336), 'kind': 'str', 'page': 1, 'name': 'table1.row1.col1'},
            {'bbox': (33.333333333333336, 0.0, 66.66666666666667, 33.333333333333336), 'kind': 'int', 'page': 1, 'name': 'table1.row1.col2'},
            {'bbox': (66.66666666666667, 0.0, 100.0, 33.333333333333336), 'kind': 'float', 'page': 1, 'name': 'table1.row1.col3'},
            {'bbox': (0.0, 33.333333333333336, 33.333333333333336, 66.66666666666667), 'kind': 'str', 'page': 1, 'name': 'table1.row2.col1'},
            {'bbox': (33.333333333333336, 33.333333333333336, 66.66666666666667, 66.66666666666667), 'kind': 'int', 'page': 1, 'name': 'table1.row2.col2'},
            {'bbox': (66.66666666666667, 33.333333333333336, 100.0, 66.66666666666667), 'kind': 'float', 'page': 1, 'name': 'table1.row2.col3'},
            {'bbox': (0.0, 66.66666666666667, 33.333333333333336, 100.0), 'kind': 'str', 'page': 1, 'name': 'table1.row3.col1'},
            {'bbox': (33.333333333333336, 66.66666666666667, 66.66666666666667, 100.0), 'kind': 'int', 'page': 1, 'name': 'table1.row3.col2'},
            {'bbox': (66.66666666666667, 66.66666666666667, 100.0, 100.0), 'kind': 'float', 'page': 1, 'name': 'table1.row3.col3'},
        ]

        table2_expected_fields = [
            {'bbox': (10.0, 10.0, 43.333333333333336, 43.333333333333336), 'kind': 'str', 'page': 2, 'name': 'table2.row1.col1'},
            {'bbox': (43.333333333333336, 10.0, 76.66666666666667, 43.333333333333336), 'kind': 'int', 'page': 2, 'name': 'table2.row1.col2'},
            {'bbox': (76.66666666666667, 10.0, 110.0, 43.333333333333336), 'kind': 'float', 'page': 2, 'name': 'table2.row1.col3'},
            {'bbox': (10.0, 43.333333333333336, 43.333333333333336, 76.66666666666667, 43.333333333333336), 'kind': 'str', 'page': 2, 'name': 'table2.row2.col1'},
            {'bbox': (43.333333333333336, 43.333333333333336, 76.66666666666667, 76.66666666666667), 'kind': 'int', 'page': 2, 'name': 'table2.row2.col2'},
            {'bbox': (76.66666666666667, 43.333333333333336, 110.0, 76.66666666666667), 'kind': 'float', 'page': 2, 'name': 'table2.row2.col3'},
            {'bbox': (10.0, 76.66666666666667, 43.333333333333336, 110.0), 'kind': 'str', 'page': 2, 'name': 'table2.row3.col1'},
            {'bbox': (43.333333333333336, 76.66666666666667, 76.66666666666667, 110.0), 'kind': 'int', 'page': 2, 'name': 'table2.row3.col2'},
            {'bbox': (76.66666666666667, 76.66666666666667, 110.0, 110.0), 'kind': 'float', 'page': 2, 'name': 'table2.row3.col3'},
        ]

        # Test for table1
        table1_fields = config.create_table_fields('table1', config_data['table1'])
        self.assertEqual(len(table1_fields), len(table1_expected_fields))
        for field, expected_field in zip(table1_fields, table1_expected_fields):
            self.assertAlmostEqual(field['bbox'][0], expected_field['bbox'][0], places=3)
            self.assertAlmostEqual(field['bbox'][1], expected_field['bbox'][1], places=3)
            self.assertAlmostEqual(field['bbox'][2], expected_field['bbox'][2], places=3)
            self.assertAlmostEqual(field['bbox'][3], expected_field['bbox'][3], places=3)
            self.assertEqual(field['kind'], expected_field['kind'])
            self.assertEqual(field['page'], expected_field['page'])
            self.assertEqual(field['name'], expected_field['name'])

        # Test for table2
        table2_fields = config.create_table_fields('table2', config_data['table2'])
        self.assertEqual(len(table2_fields), len(table2_expected_fields))
        for field, expected_field in zip(table2_fields, table2_expected_fields):
            self.assertAlmostEqual(field['bbox'][0], expected_field['bbox'][0], places=3)
            self.assertAlmostEqual(field['bbox'][1], expected_field['bbox'][1], places=3)
            self.assertAlmostEqual(field['bbox'][2], expected_field['bbox'][2], places=3)
            self.assertAlmostEqual(field['bbox'][3], expected_field['bbox'][3], places=3)
            self.assertEqual(field['kind'], expected_field['kind'])
            self.assertEqual(field['page'], expected_field['page'])
            self.assertEqual(field['name'], expected_field['name'])

        
if __name__ == '__main__':
    unittest.main()
