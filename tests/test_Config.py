import os
import unittest
from e_pdf_form_reader.Config import Config


class TestConfig1(unittest.TestCase):
    
    def setUp(self):
        # Inizializza eventuali variabili o oggetti necessari per i test
        self.config = Config()
        self.data = {
            'up-left': (0, 0),
            'down-right': (100, 100),
            'rows': 'A01-03',
        }

    def test_get_kind(self):
        # Testa il metodo get_kind() con vari casi
        
        # Caso in cui il tipo è specificato
        name = "example(int)"
        result = self.config.get_kind(name)
        self.assertEqual(result, ("example", "int"))

        # Caso in cui il tipo non è specificato
        name = "example"
        result = self.config.get_kind(name)
        self.assertEqual(result, ("example", "str"))

    def test_expand_range_with_colon(self):
        # Testa il metodo expand_range_with_colon() con vari casi
        data = {
            'up-left': (0, 0),
            'down-right': (100, 100),
            'rows': 'A01 :50: A02 :75: A03',
        }        
        result = self.config.expand_range_with_colon(data, "rows")
        expected_result = [('A01', 'str', 0, 50), ('A02', 'str', 50, 75), ('A03', 'str', 75, 100)]
        self.assertEqual(result, expected_result)

    def test_expand_range_with_colon2(self):
        # Testa il metodo expand_range_with_colon() con vari casi
        data = {
            'up-left': (0, 0),
            'down-right': (100, 100),
            'rows': 'A01 :25: A02-03 :75: A04',
        }        
        result = self.config.expand_range_with_colon(data, "rows")
        expected_result = [('A01', 'str', 0, 25), ('A02', 'str', 25, 50), ('A03', 'str', 50, 75), ('A04', 'str', 75, 100)]
        self.assertEqual(result, expected_result)

    def test_expand_range_with_comma(self):
        # Testa il metodo expand_range_with_comma() con vari casi
        result = self.config.expand_range_with_comma(self.data, "rows")
        expected_result = [('A01', 'str', 0, 33.333333333333336), ('A02', 'str', 33.333333333333336, 66.66666666666667), ('A03', 'str', 66.66666666666667, 100)]
        self.assertEqual(result, expected_result)

    def test_expand_range_part(self):
        # Testa il metodo expand_range_part() con vari casi
        part = "A01-03"
        result = self.config.expand_range_part(part)
        expected_result = ['A01', 'A02', 'A03']
        self.assertEqual(result, expected_result)



class TestConfig(unittest.TestCase):

    def setUp(self):
        # Prepara una configurazione di test
        self.config_data = {
            'field1': {'up-left': '0,0', 'down-right': '100,100', 'page': '1', 'kind': 'single'},
            'field2': {'up-left': '10,10', 'down-right': '110,110', 'page': '2', 'cast': 'float', 'kind': 'single'},
            'field3': {'up-left': '20,20', 'down-right': '120,120', 'page': '3', 'cast': 'date', 'kind': 'single'},
        }
        self.config = Config()
        self.config.config_data = self.config_data
        
    def test_config_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Config("non_existent_config.ini")
            
    def test_load_config(self):
        module_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(module_dir, "test_config.ini")
        config = Config(config_file)
        expected_config_data = {'Section1': {'key1': 'value1', 'key2': 'value2'}, 'Section2': {'key3': 'value3'}}
        self.assertEqual(config.config_data, expected_config_data)

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
        data1 = {'up-left': (0,0), 'down-right': (100,100), 'page': 1, 'kind' : 'single' } 
        field_data1 = self.config.process_single_data('field1', data1)
        self.assertEqual(len(field_data1), 1)
        self.assertEqual(field_data1[0]['bbox'], (0.0, 0.0, 100.0, 100.0))
        self.assertEqual(field_data1[0]['kind'], 'str')
        self.assertEqual(field_data1[0]['page'], 1)
        self.assertEqual(field_data1[0]['name'], 'field1')

        data2 = {'up-left': (0,0), 'down-right': (100,100), 'page': 1, 'kind' : 'single', 'cast': 'float' } 
        field_data2 = self.config.process_single_data('field2', data2)
        self.assertEqual(field_data2[0]['kind'], 'float')

        data3 = {'up-left': (0,0), 'down-right': (100,100), 'page': 1, 'kind' : 'single', 'cast': 'date' } 
        field_data3 = self.config.process_single_data('field3', data3)
        self.assertEqual(field_data3[0]['kind'], 'date')

    def test_expand_range(self):
        data = {
            'up-left': (0,0), 'down-right': (100,100),
            'rows': 'row1,row2,row3'
        }
        rows = [('row1', 'str', 0, 33.333333333333336),
                ('row2', 'str', 33.333333333333336, 66.66666666666667),
                ('row3', 'str', 66.66666666666667, 100.0)]
        expanded_rows = self.config.expand_range(data,'rows')
        self.assertEqual(expanded_rows, rows)

        data['rows'] = 'row1,row2-5,row6'
        rows = [('row1', 'str', 0, 16.666666666666668), ('row2', 'str', 16.666666666666668, 33.333333333333336),
                ('row3', 'str', 33.333333333333336, 50.0), ('row4', 'str', 50.0, 66.66666666666667),
                ('row5', 'str', 66.66666666666667, 83.33333333333334), ('row6', 'str', 83.33333333333334, 100.00000000000001)]
        expanded_rows = self.config.expand_range(data,'rows')
        self.assertEqual(expanded_rows, rows)

        
    def test_expand_range1(self):
        for row in [ 'A,B,C',
                     'Ass.C(bool) :34: Ass.F(bool) :45: Codice :83: Descrizione :250: Periodo :340: Val.Unitario :390: Dato.1 :400: X',
                     'Ass.C(bool) :34: Ass.F(bool) :45: Codice :83: Descrizione :250: Periodo :340: Val.Unitario :390: Dato.1 :400: Importo(float)',
                     'C,NC',
                     'CUP.AC,CUP.NAC,F.AC(int),F.NAC(int)',
                     'DecorrenzaG(date) :500: DecorrenzaE(date)',
                     'EL(float) :100: RC(float) :170: RFC(float) :245: RF(float) :320: N(float) :390: RRC(float) :470: NAP(float)',
                     'INPS(float),A.INPS(float),INPDAP(float),INPS.OM(float)',
                     'INPS(float),A.INPS(float),INPDAP.asc(float),INPDAP.cc(float),TLP.INPS(float)',
                     'Imponibile(float) :190: Imposta.Lorda(float) :260: Coniuge :310: Figli.N(int) :325: Figli.Importo(float) :375: X',
                     'MAC,AP,PRO',
                     'MAC,PAC,AP,PAP',
                     'R01,R02,R03,R04,R05,R06,R07,R08,R09,R10,R11,R12,R13,R14',
                     'Segmento :150: DecorrenzaS(date) :240: Fascia :255: DecorrenzaF(date) :330: Livello :360: DecorrenzaL(date)',
                     'X,Y']:
            data = {
                'up-left': (0,0),
                'down-right': (1000,1000),
                'rows': row
            }
            expanded_rows = self.config.expand_range(data,'rows')
        
    def test_create_multi_row_fields(self):
        # Test con righe specifiche
        data1 = {'up-left': (0,0), 'down-right': (100,100),
                 'page': '1',
                 'rows': (("row1","str",0,50),("row2","str",50,100)),
                 'columns': (("X","str",0,50),("Y","str",50,100))}
        fields1 = self.config.create_multi_row_fields('section1', data1)
        self.assertEqual(len(fields1), 4)
        self.assertEqual(fields1[0]['name'], '.row1.X')
        self.assertEqual(fields1[1]['name'], '.row1.Y')
        self.assertEqual(fields1[2]['name'], '.row2.X')

        # Test con tipo di campo diverso
        data2 = {'up-left': (0,0), 'down-right': (100,100),
                 'page': '1',
                 'rows': (("row1","str",0,50),("row2","str",50,100)),
                 'columns': (("X","float",0,50),("Y","int",50,100))}
        fields2 = self.config.create_multi_row_fields('section2', data2)
        self.assertEqual(len(fields2), 4)
        self.assertEqual(fields2[0]['kind'], 'float')
        self.assertEqual(fields2[1]['kind'], 'int')
        self.assertEqual(fields2[2]['kind'], 'float')

        # Test con prefisso di gruppo
        data4 = {'up-left': (0,0), 'down-right': (100,100),
                 'page': '1', 'group': 'group1',
                 'rows': (("row1","str",0,50),("row2","str",50,100)),
                 'columns': (("X","float",0,50),("Y","int",50,100))}
        fields4 = self.config.create_multi_row_fields('section4', data4)
        self.assertEqual(len(fields4), 4)
        self.assertEqual(fields4[0]['name'], 'group1.row1.X')
        self.assertEqual(fields4[1]['name'], 'group1.row1.Y')
        self.assertEqual(fields4[2]['name'], 'group1.row2.X')
        
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
            'table1':  {'up-left': (0,0), 'down-right': (100,100),
                        'page': 1, 'group': 'group1',
                        'rows': (("row1","str",0,50),("row2","str",50,100)),
                        'columns': (("X","float",0,50),("Y","int",50,100))},
            'table2': {'up-left': (10,10), 'down-right': (110,110),
                        'page': 1, 'group': 'group1',
                        'rows': (("row1","str",10,60),("row2","str",60,110)),
                        'columns': (("X","float",10,60),("Y","int",60,110))}
        }

        config = Config()
        config.config_data = config_data

        table1_expected_fields = [{'bbox': (0, 0, 50, 50), 'kind': 'float', 'name': 'group1.row1.X', 'page': 1},
                                  {'bbox': (50, 0, 100, 50), 'kind': 'int', 'name': 'group1.row1.Y', 'page': 1},
                                  {'bbox': (0, 50, 50, 100),
                                   'kind': 'float',
                                   'name': 'group1.row2.X',
                                   'page': 1},
                                  {'bbox': (50, 50, 100, 100),
                                   'kind': 'int',
                                   'name': 'group1.row2.Y',
                                   'page': 1}]

        table2_expected_fields = [{'bbox': (10, 10, 60, 60),
                                   'kind': 'float',
                                   'name': 'group1.row1.X',
                                   'page': 1},
                                  {'bbox': (60, 10, 110, 60), 'kind': 'int', 'name': 'group1.row1.Y', 'page': 1},
                                  {'bbox': (10, 60, 60, 110),
                                   'kind': 'float',
                                   'name': 'group1.row2.X',
                                   'page': 1},
                                  {'bbox': (60, 60, 110, 110),
                                   'kind': 'int',
                                   'name': 'group1.row2.Y',
                                   'page': 1}]

        # Test for table1
        table1_fields = config.process_table_data('table1', config_data['table1'])
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
        table2_fields = config.process_table_data('table2', config_data['table2'])
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
