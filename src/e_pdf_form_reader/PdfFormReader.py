import fitz
import logging
import re
from datetime import datetime
from pprint import pformat

from .DataProcessor import DataProcessor

class PdfFormReader:
    """
    Represents a PDF file and provides methods to extract text with bounding boxes.
    """
    A4 = (595.2755905511812, 841.8897637795277)

    def __init__(self, pdf_path):
        """
        Initializes the Pdf object with the path to the PDF file.
        """
        self.path = pdf_path
        try:
            self.document = fitz.open(self.path)
        except Exception as e:
            logging.error(f"Unable to open the PDF file '{self.path}': {e}")
            raise ValueError("Unable to open the PDF file")

        self.read_boxes()

    def read_boxes(self):
        """
        Reads the text and bounding boxes from each page of the PDF.
        """
        text_with_bbox = []
        for page_num in range(len(self.document)):
            page = self.document.load_page(page_num)
            words = page.get_text('words')
            for word in words:
                x0, y0, x1, y1 = word[:4]
                text = word[4]
                text_with_bbox.append({
                    'load': text,
                    'bbox': {
                        'x0': self.A4[0] - x1,
                        'y0': self.A4[1] - y1,
                        'x1': self.A4[0] - x0,
                        'y1': self.A4[1] - y0,
                    },
                    'page': page_num + 1
                })
        self.document.close()
        self.boxes = sorted(text_with_bbox,
                            key=lambda x: (x['page'], x['bbox']['y0'], x['bbox']['x0']))

    def get(self, page, area, kind='str'):
        """
        Retrieves text within the specified bounding box on the given page.
        """
        try:
            result = self._retrieve_text(page, area)
            result = self._process_text(result, kind)
        except Exception as e:
            logging.error(f"Error occurred while retrieving text: {e}")
            result = {'error': str(e)}

        return result

    def _retrieve_text(self, page, area):
        """
        Retrieves text within the specified bounding box on the given page.
        """
        result = {'bbox': area, 'load': "", 'page': page}
        for box in sorted(self.boxes,
                          key=lambda x: (x['page'], x['bbox']['y0'], x['bbox']['x0'])):
            if box['page'] != page:
                continue
            if (area[0] <= box['bbox']['x0'] <= area[2] and
                    (area[1] - (area[3] - area[1]) * 1 / 10) <= box['bbox']['y0'] <= area[1] + (area[3] - area[1]) * 3 / 4):
                result['load'] = (result['load'] + ' ' + box['load']).strip()

        return result

    def _process_text(self, result, kind):
        """
        Process the retrieved text based on the specified kind.
        """
        load = result['load']
        if len(load) > 0:
            if re.search(r"(?<!-)-$", result['load']):
                result['load'] = "-" + result['load'][:-1].strip()
            try:
                if kind == 'int':
                    result['load'] = int(result['load'])
                elif kind == 'bool':
                    result['load'] = True if len(result['load']) > 0 else False
                elif re.match('^date', kind):
                    formato = "%d/%m/%Y"
                    m = re.match("^date (.+)", kind)
                    if m:
                        formato = m.group(1)
                    result['load'] = datetime.strptime(result['load'], formato).strftime("%Y/%m/%d")
                elif kind == 'float':
                    load = re.sub(",", ".", re.sub("\.", "", result['load']))
                    result['load'] = float(load)
            except Exception as e:
                logging.error(f"Error occurred while processing text: {e}")
                result['load'] = load

        return result

    def get_results(self, groups, debug=False):
        """
        Retrieves results based on the provided groups configuration.

        Args:
            groups (list): The list of group configuration data.

        Returns:
            list: The list of extracted results.
        """
        results = []
        for group in groups:
            logging.debug(f"Reading {group['group']}")
            stop_at = None
            active = True
            start_at = None
            if 'stop-at' in group:
                stop_at = re.split(r"\s*==\s*", group['stop-at'])
            if 'start-at' in group:
                start_at = re.split(r"\s*==\s*", group['start-at'])
                active = False
            box_line = []
            for field in group['fields']:
                logging.debug(f"Reading {group['group']} FIELD {field['name']} : {field['page']}/{field['bbox']}")
                bbox = field['bbox']
                name = field['name']
                page = field['page']
                try:
                    box = self.get(page, bbox, kind=field['kind'])
                except Exception as e:
                    logging.error(f"Error occurred while processing field: {field['name']}: {e}")
                if box['load']:
                    if start_at and re.match(f"{group['group']}\..*\.{start_at[0]}", name) and re.match(start_at[1], box['load']):
                        active = True
                    if stop_at and re.match(f"{group['group']}\..*\.{stop_at[0]}", name) and re.match(stop_at[1], box['load']):
                        break
                    if active:
                        field.update(box)
                        box_line.append(field)
            if box_line:
                try:
                    group = DataProcessor.cast(group, box_line)
                except Exception as e:
                    logging.error(f"Error occurred while processing group: {group['group']}: {e}")
                results.extend(group['fields'])
        if debug:
            self.save_results_to_file(results)
        return results

        
    def save_results_to_file(self, results, output_file='/tmp/pdf_results.json'):
        """
        Saves the results of the get_results function to a JSON file.

        Args:
            results (list): The list of extracted results.
            output_file (str): The path to the output JSON file (default: '/tmp/pdf_results.json').
        """
        try:
            import json
            with open(output_file, 'w') as json_file:
                json.dump(results, json_file, indent=4)
            logging.info(f"Results saved to '{output_file}'")
        except Exception as e:
            logging.error(f"Error occurred while saving results to '{output_file}': {e}")
