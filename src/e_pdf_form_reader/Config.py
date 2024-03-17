import traceback
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
            self.load_config(config_file)
        self.field_model = None

    def load_config(self, config_file=None):
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
        return config_data

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

    def process_single_data(self, section, data):
        """
        Creates single fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of single fields.
        """
        x0, y0 = data['up-left']
        x1, y1 = data['down-right']
        bbox = (x0, y0, x1, y1)
        field_name = (data.get('group') + '.' if data.get('group', None) else "") + section
        field_type = data.get('cast', 'str')
        field_page = data.get('page')
        return [{'bbox': bbox, 'kind': field_type, 'page': field_page, 'name': field_name}]
        
    def create_single_row_fields(self, data, x0, y0, x1, y1, label=None):
        fields = []
        columns = data['columns']
        label = data.get('group', '') + ("." + label) if label else ""
        for field,kind,x0,x1 in columns:
            fields.append({
                'bbox': (x0, y0, x1, y1),
                'kind': kind,
                'page': data.get('page'),
                'name': label + '.' + field
            })
        return fields
        
    def create_multi_row_fields(self, section, data):
        """
        Creates multi-row fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of multi-row fields.
        """
        rows = data['rows']
        x0, y0 = data['up-left']
        x1, y1 = data['down-right']
        bbox = [ x0, y0, x1, y1 ]
        
        n_rows = len(rows)
        # y_rows = [ y0 + n * (y1 - y0) / n_rows for n in range(1,n_rows + 1) ]

        multi_row_fields = []
        for field,kind,y0,y1 in rows:
            field_data = self.create_single_row_fields(data, x0, y0, x1, y1,label=field)
            multi_row_fields.extend(field_data)

        return multi_row_fields

    def get_kind(self, name):
        """
        Parses the field type from the configuration field name.
        """
        m = re.match(r"([\w\.-]+)(?:\((int|bool|float|str|date(?: [%a-zA-Z]+)?)\))?", name)
        if m:
            x, k = m.groups()
            if k is None:
                k = "str"
            else:
                k = k
            return x, k

    def expand_range(self, data, field):
        if field in data:
            value = data[field]
            if ',' in value:
                return self.expand_range_with_comma(data,field)
            elif ':' in value:
                return self.expand_range_with_colon(data,field)
            else:
                name, kind = self.get_kind(data[field])
                if field == "rows":
                    return [(name, kind, data['up-left'][1], data['down-right'][1]),]
                else:
                    return [(name, kind, data['up-left'][0], data['down-right'][0]),]
        
    def expand_range_with_colon(self, data, field):
        value = data.get(field,'A')
        parts = []
        x0, y0 = data['up-left']
        x1, y1 = data['down-right']        
        d0 = y0 if field == "rows" else x0
        dF = y1 if field == "rows" else x1        
        dividers = re.split(r"\s*:\s*", value)
        while dividers:
            print(dividers)
            element = dividers.pop(0)
            field, kind = self.get_kind(element)            
            if dividers:
                d1 = float(dividers.pop(0))
            else:
                d1 = dF
            if '-' in field:
                fields = self.expand_range_part(field)
            else:                
                fields = [field,]
            delta = (d1 - d0) / len(fields)                
            for field in fields:
                d1 = d0 + delta
                parts.append( (field, kind, d0, d1 ) )
                d0 = d1                
        return parts
        
    def expand_range_with_comma(self, data, field):
        x0, y0 = data['up-left']
        x1, y1 = data['down-right']        
        d0 = y0 if field == "rows" else x0
        dF = y1 if field == "rows" else x1
        parts = data.get(field,"X")
        if ',' in parts:
            parts = re.split(r"\s*,\s*",parts)
        else:
            parts = [ parts, ]
        expanded = []
        for part in parts:
            expanded.extend(self.expand_range_part(part))
        delta = (dF - d0) / len(expanded)
        rows = []
        for row in expanded:
            name, kind = self.get_kind(row)
            d1 = d0 + delta
            rows.append( (name, kind, d0, d1 ) )
            d0 = d1
        return rows

    def expand_range_part(self, part):
        if '-' not in part:
            return [part,]
        m = re.match(r"^([\w\.]+)([0-9]+)-([0-9]+)$", part)
        if not m:
            return [part,]
        prefix, start, end = m.groups()
        n_zeros = len(start) - len(str(int(start)))
        start, end = int(start), int(end)
        if end < start:
            logging.error(f'Part range error {end}<{start}')
            return []
        return [f"{prefix}{str(i).zfill(n_zeros - len(str(i)))}" for i in range(start, end + 1)]
    
    def process_row_data(self, section, data):
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

        fields = self.create_multi_row_fields(section, data)

        return fields

    def process_table_data(self, section, data):
        """
        Creates table fields based on the provided configuration data.

        Args:
            section (str): The section name in the configuration file.
            data (dict): The configuration data for the section.

        Returns:
            list: The list of table fields.
        """
        x0, y0 = data['up-left']
        x1, y1 = data['down-right']        

        rows = data.get('rows')
        columns = data.get('columns')

        print(section,columns)
        num_rows = len(rows)
        num_columns = len(columns)

        # Calculate bounding boxes for each cell in the table
        cell_width = (x1 - x0) / num_columns
        cell_height = (y1 - y0) / num_rows

        fields = []
        prefix = data.get('group') or section

        page = data.get('page')
        priority = data.get('priority','col')
        
        for row, (row_name, row_type, y0, y1) in enumerate(rows):
            for col, (col_name, col_type, x0, x1) in enumerate(columns):
                fields.append({
                    'bbox': (x0, y0, x1, y1),
                    'kind': col_type if priority == 'col' else row_type,
                    'page': page,
                    'name': f"{prefix}.{row_name}.{col_name}"
                })

        return fields
        
    def check_data_struct(self, section, data):
        errors = []
        warnings = []
        missing_keys = self.check_mandatory_keys(data, 'kind', 'page', 'up-left', 'down-right')
        if missing_keys:
            errors.append((section,f"Missing mandatory keys {','.join(missing_keys)}'"))
        if data['kind'] not in ('row','table', 'single'):
            errors.append((section,f"Kind mismatch: {data['kind']}"))
        else:
            if data['kind'] == 'row':
                missing_keys = self.check_mandatory_keys(data, 'columns')
                if missing_keys:
                    errors.append((section, f"Missing mandatory keys {','.join(missing_keys)}"))
            if data['kind'] == 'table':
                missing_keys = self.check_mandatory_keys(data, 'rows', 'columns')
                if missing_keys:
                    errors.append((section, f"Missing mandatory keys {','.join(missing_keys)}"))
        if ',' not in data['up-left'] or ',' not in data['down-right']:
                errors.append((section, f"Missing mandatory keys {','.join(missing_keys)}"))
        up_left = tuple(map(float, data['up-left'].split(',')))
        down_right = tuple(map(float, data['down-right'].split(',')))
        if len(up_left) < 2:
            errors.append((section, f"Not enough values in up-left '{data['up-left']}'"))
        if len(down_right) < 2:
            errors.append((section, f"Not enough values in down-right '{data['down-right']}'"))
        if len(errors) == 0:
            data['up-left'] = up_left
            data['down-right'] = down_right
        if 'rows' in data:
            try:
                rows = self.expand_range(data,'rows')
            except Exception as e:
                errors.append((section, f"Rows definition mismatch '{data['rows']}' ({e} {traceback.format_exc()})"))
        if 'columns' in data:
            try:
                columns = self.expand_range(data,'columns')
            except Exception as e:
                errors.append((section,f"Columns definition mismatch '{data['columns']}' ({e} {traceback.format_exc()})"))
        try:
            page = int(data.get("page"))
        except Exception as e:
            errors.append((section, f"Page not integer '{data['page']}'"))
            
        if 'group' not in data:
            warnings.append((section, f"No 'group' key"))
        if 'result' not in data:
            warnings.append((section, f"No 'result' key"))
            
        if len(errors) == 0:
            data['up-left'] = up_left
            data['down-right'] = down_right
            if 'rows' in locals():
                data['rows'] = rows
            if 'columns' in locals():
                data['columns'] = columns
            if 'page' in locals():
                data['page'] = page
        else:
            self.printout_errors(errors,warnings)
        return data, errors, warnings
    
    def printout_errors(self,errors,warnings):
        for section, warn in warnings:
            print(f"WARNING in section {section}: {warn}")
        for section, error in errors:
            print(f"  ERROR in section {section}: {error}")

    def create_field_model(self, debug=False):
        """
        Creates a structured field model from the configuration data.

        Returns:
            list: The structured field model.
        """
        info = []
        in_error = False
        for section, data in self.config_data.items():
            data, error, warnings = self.check_data_struct(section, data)
            if error:
                in_error = True
            if in_error:
                continue
            kind = data.get('kind')
            if kind == 'single':
                data['fields'] = self.process_single_data(section, data)
            elif kind == 'row':
                data['fields'] = self.process_row_data(section, data)
            elif kind == "table":
                data['fields'] = self.process_table_data(section, data)
            info.append(data)
        if in_error:
            raise ValueError(f"Errors for configuration file")      
        self.field_model = sorted(info, key=lambda data:data['up-left'])
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
