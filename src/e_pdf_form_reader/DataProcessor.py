import json
import logging
import re

class DataProcessor:
    """
    Utility class for processing PDF data.
    """

    @staticmethod
    def save_to_json(data, output_file):
        """
        Saves the data to a JSON file.

        Args:
            data (dict): The data to be saved.
            output_file (str): The path to the output JSON file.
            
        Raises:
            IOError: If an error occurs while writing to the JSON file.
        """
        try:
            with open(output_file, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except IOError as e:
            logging.error(f"Unable to save data to '{output_file}': {e}")

    @staticmethod
    def _update_bbox(bbox, field_bbox):
        """
        Updates bounding box coordinates based on field_bbox.

        Args:
            bbox (tuple): Current bounding box coordinates.
            field_bbox (tuple): Bounding box coordinates of the field.

        Returns:
            tuple: Updated bounding box coordinates.
        """
        min_x, min_y, max_x, max_y = bbox
        min_x = min(min_x, field_bbox[0])
        max_x = max(max_x, field_bbox[2])
        min_y = min(min_y, field_bbox[1])
        max_y = max(max_y, field_bbox[3])
        return min_x, min_y, max_x, max_y

    @staticmethod
    def cast(group, fields):
        result = group.get("result","text")
        if result == 'list':
            fields = DataProcessor._cast_to_list(fields)
        elif result == 'text':
            fields = DataProcessor._cast_to_text(fields)
        elif result == 'dict':
            fields = DataProcessor._cast_to_dict(fields)
        elif re.match('row_dict',result):
            m = re.match("row_dict\(\s*([\w\.]+)\s*\)",result)
            if m:
                prefix = m.group(1)
                fields = DataProcessor._cast_to_rowdict(fields, prefix)
        else:
            newf = []
            for f in fields:
                newf.append({ "kind": f['kind'], 'load': f['load'] })
            fields = newf
        group['fields'] = fields
        return group

    @staticmethod
    def _cast_to_list(fields):
        field = {}
        field['kind'] = 'list'
        field['load'] = ( f['load'] for f in fields )
        return (field,)

    @staticmethod
    def _cast_to_dict(fields):
        field = {}
        field['kind'] = 'dict'
        field['load'] = { f['name'] : f['load'] for f in fields }
        return (field,)

    @staticmethod
    def _cast_to_rowdict(fields,prefix):
        field = {}
        field['kind'] = 'rowdict'
        field['load'] = {}
        for f in fields:
            name, rest = f['name'][len(prefix)+1:].split(".",1)
            if name not in field['load']:
                field['load'][name] = {}
            field['load'][name][rest] = f['load']
        return (field,)

    @staticmethod
    def _cast_to_text(fields):
        fields = DataProcessor._cast_to_list(fields)
        fields[0]['load'] = "\n".join(fields[0]['load'])
        fields[0]['kind'] = "text"
        return fields

    
    @staticmethod
    def refile_results(results, keyname="Codice"):
        """
        Refiles the extracted results based on the specified key name.

        Args:
            results (list): The list of extracted results.
            keyname (str): The key name to use for re-filing.

        Returns:
            dict: The re-filed results.
        """
        keystore = {}
        for num, result in enumerate(results):
            kind = result['kind']
            load = result['load']            
            if kind == 'rowdict':
                for key, row in load.items():
                    code = row.get(keyname, f"RD{num:04d}.{key}")
                    for field, value in row.items():
                        keystore[f"SCR.{code}.{field}"] = value
            elif kind == 'dict':
                keystore.update(load)
            elif kind == 'text':
                keystore[f"TXT.{load}"] = load
            else:
                if 'name' in result:
                    keystore[result['name']] = load
                else:
                    keystore[f"KEY-{num}"] = load
        return keystore
