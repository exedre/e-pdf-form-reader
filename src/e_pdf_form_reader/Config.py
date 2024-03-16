import os
import re
import logging
from collections import defaultdict
import configparser

class Config:
    """
    Represents the configuration data for extracting text fields from PDFs.

    Attributes:
        config_file (str): The path to the configuration file.
        config_data (dict): The loaded configuration data.
        field_model (list): The structured field model created from the configuration data.
    """

    def __init__(self, config_file=None):
        """
        Initializes the configuration object with data from the provided config file.

        Args:
            config_file (str): The path to the configuration file.
        """
        self.config_file = config_file
        if config_file:
            self.config_data = self.load_config(config_file)
        self.field_model = None

    def load_config(self,config_file = None):
        """
        Loads configuration data from the specified config file.

        Args:
            config_file (str): The path to the configuration file.

        Returns:
            dict: The loaded configuration data.
        """
        config_file = config_file or self.config_file
        if not os.path.isfile(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found")
        config_data = defaultdict(dict)
        try:
            config = configparser.ConfigParser()
            config.read(config_file)
            for section in config.sections():
                for key, value in config.items(section):
                    config_data[section][key] = value
        except Exception as e:
            raise ValueError(f"Error loading configuration from '{config_file}': {e}")
        self.config_data = config_data

    def parse_field_type(self, name):
        """
        Parses the field type from the configuration field name.

        Args:
            name (str): The name of the configuration field.

        Returns:
            tuple: A tuple containing the field name and its type.
        """
        m = re.match(r"([\w\.]+)(?:\((int|bool|float|str|date(?: [\w%-]+)?)\))?", name)
        if m:
            field_name, field_type = m.groups()
            field_type = field_type if field_type else "str"
            return field_name, field_type

    def check_mandatory_keys(self, data, *keys):
        """
        Checks if mandatory keys are present in the configuration data.

        Args:
            data (dict): The configuration data to check.
            *keys: The mandatory keys to check for.

        Returns:
            list: A list of missing mandatory keys.
        """
        return [key for key in keys if key not in data]

    def create_single_field(self, section, data):
        """
        Creates single fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of single fields.
        """
        up_left = tuple(map(float, data['up-left'].split(',')))
        down_right = tuple(map(float, data['down-right'].split(',')))
        x0, y0 = up_left
        x1, y1 = down_right
        bbox = (x0, y0, x1, y1)
        field_name = (data.get('group') + '.' if data.get('group',None) else "") + section
        field_type = data.get('cast', 'str')
        field_page = int(data.get('page'))
        return [{'bbox': bbox, 'kind': field_type, 'page': field_page, 'name': field_name}]

    def create_single_row_fields(self,data,x0,y0,xF1,y1, label=None):
        fields = []
        dividers = re.split(r"\s*:\s*", data['columns'])
        label = data.get('group', '') + ( "." + label ) if label else ""        
        while dividers:
            field, kind = self.get_kind(dividers.pop(0))
            if dividers:
                x1 = int(dividers.pop(0))
            else:
                x1 = xF1
            fields.append({
                'bbox': (x0, y0, x1, y1),
                'kind': kind,
                'page': int(data.get('page')),
                'name': label + '.' + field
            })
            x0 = x1
        return fields
        
    def create_multi_row_fields(self, section, data, rows):
        """
        Creates multi-row fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of multi-row fields.
        """
        up_left = tuple(map(float, data['up-left'].split(',')))
        down_right = tuple(map(float, data['down-right'].split(',')))
        x0, y0 = up_left
        x1, y1 = down_right
        bbox = [x0, y0, x1, y1]

        n_rows = len(rows)
        y_rows = [ y0 + n * (y1 - y0) / n_rows for n in range(1,n_rows + 1) ]

        multi_row_fields = []
        for n_row,y1 in enumerate(y_rows):
            field_data = self.create_single_row_fields(data, x0, y0, x1, y1,label=rows[n_row])
            y0 = y1
            multi_row_fields.extend(field_data)

        return multi_row_fields

    def get_kind(self, name):
        """
        Parses the field type from the configuration field name.
        """
        m = re.match(r"([\w\.]+)(?:\((int|bool|float|str|date(?: [%a-zA-Z]+)?)\))?", name)
        if m:
            x, k = m.groups()
            if k is None:
                k = "str"
            else:
                k = k
            return x, k
    
    def expand_row_range(self, rows):
        """
        Expands row ranges specified in the configuration data.

        Args:
            rows (tuple): The row range specified in the configuration data.

        Returns:
            list: The expanded row range.
        """
        expanded_rows = []
        for row in rows:
            if '-' in row:
                expanded_rows.extend(self.expand_single_row_range(row))
            else:
                expanded_rows.append(row)
        return expanded_rows

    def expand_single_row_range(self, row):
        """
        Expands a single row range specified in the configuration data.

        Args:
            row (str): The single row range specified in the configuration data.

        Returns:
            list: The expanded single row range.
        """
        prefix, start, end = re.match(r"^([\w\.]+)([0-9]+)-([0-9]+)$", row).groups()
        n_zeros = len(start) - len(str(int(start)))
        start, end = int(start), int(end)
        if end < start:
            logging.error(f'Row range error {end}<{start}')
            return []
        return [f"{prefix}{str(i).zfill(n_zeros - len(str(i)))}" for i in range(start, end + 1)]
    
    def process_row_kind(self, section, data):
        """
        Processes configuration data for rows.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The fields created from the row configuration.
        """
        missing = self.check_mandatory_keys(data, 'columns')
        if missing:
            logging.error(f"Missing mandatory '{missing}' key in section '{section}'")
            return []

        if 'rows' in data:        
            rows = tuple(data['rows'].split(','))
            if '-' in data['rows']:
                rows = self.expand_row_range(rows)
            fields = self.create_multi_row_fields(section, data, rows)
        else:
            fields = self.create_multi_row_fields(section, data, ['ROW1'])

        return fields

    def create_table_fields(self, section, data):
        """
        Creates table fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of table fields.
        """
        up_left = tuple(map(float, data['up-left'].split(',')))
        down_right = tuple(map(float, data['down-right'].split(',')))
        x0, y0 = up_left
        x1, y1 = down_right

        rows = list(map(lambda x: self.get_kind(x), re.split(r"\s*,\s*", data.get('rows'))))
        columns = list(map(lambda x: self.get_kind(x), re.split(r"\s*,\s*", data.get('columns'))))

        num_rows = len(rows)
        num_columns = len(columns)

        # Calculate bounding boxes for each cell in the table
        cell_width = (x1 - x0) / num_columns
        cell_height = (y1 - y0) / num_rows

        fields = []
        prefix = data.get('group') or section

        for row, (row_name, row_type) in enumerate(rows):
            for col, (col_name, col_type) in enumerate(columns):
                cell_x0 = x0 + col * cell_width
                cell_y0 = y0 + row * cell_height
                cell_x1 = cell_x0 + cell_width
                cell_y1 = cell_y0 + cell_height
                fields.append({
                    'bbox': (cell_x0, cell_y0, cell_x1, cell_y1),
                    'kind': col_type,
                    'page': int(data.get('page')),
                    'name': f"{prefix}.{row_name}.{col_name}"
                })

        return fields
    
    
    def create_field_model(self, debug=False):
        """
        Creates a structured field model from the configuration data.

        Returns:
            list: The structured field model.
        """
        info = []
        for section, data in self.config_data.items():
            missing_keys = self.check_mandatory_keys(data, 'kind', 'page', 'up-left', 'down-right')
            if missing_keys:
                logging.error(f"Missing mandatory keys {missing_keys} in section '{section}'")
                continue
            kind = data.get('kind')
            if kind == 'single':
                data['fields'] = self.create_single_field(section, data)
            elif kind == 'row':
                data['fields'] = self.process_row_kind(section, data)
            elif kind == "table":
                data['fields'] = self.create_table_fields(section, data)
            else:
                raise ValueError(f"Kind mismatch ({kind}) for section  '{section}': {e}")                
            info.append(data)
        self.field_model = sorted(info, key=lambda data: tuple(map(int, data['up-left'].split(','))))
        if debug:
            self.dump_field_model()

    def dump_field_model(self, output_file="/tmp/field_model.json"):
        """
        Dumps the field model to a JSON file for debugging purposes.

        Args:
            output_file (str): The path to the output JSON file.

        Raises:
            IOError: If an error occurs while writing to the JSON file.
        """
        try:
            import json
            with open(output_file, 'w') as json_file:
                json.dump(self.field_model, json_file, indent=4)
        except IOError as e:
            logging.error(f"Unable to save field model to '{output_file}': {e}")        
