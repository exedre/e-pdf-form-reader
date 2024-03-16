import argparse
import logging
import os
from .Config import Config
from .DataProcessor import DataProcessor
from .PdfFormReader import PdfFormReader

logging.basicConfig(level=logging.INFO)


def evaluate_command(args):
    pdf = PdfFormReader(args.pdf_file)
    pdf_content = pdf.boxes
    DataProcessor.save_to_json(pdf_content, args.output or os.path.splitext(args.pdf_file)[0] + '-bbox.json')
    logging.info(f"Bounding box results written to '{args.output or os.path.splitext(args.pdf_file)[0] + '-bbox.json'}'.")

def read_command(args):
    if not args.config:
        logging.error("Error: The configuration file (-C/--config) is required for the 'read' command.")
        exit(1)
    if not os.path.exists(args.config):
        logging.error(f"Error: The configuration file '{args.config}' does not exist.")
        exit(1)

    pdf = PdfFormReader(args.pdf_file)
    cfg = Config(args.config)
    cfg.load_config()
    cfg.create_field_model()
    results = pdf.get_results(cfg.field_model)
    if not args.no_refile:
        results = DataProcessor.refile_results(results, args.keyname)
    
    DataProcessor.save_to_json(results, args.output or os.path.splitext(args.pdf_file)[0] + '.json')
    logging.info(f"Extraction results written to '{args.output or os.path.splitext(args.pdf_file)[0] + '.json'}'.")

    if args.bbox:
        bbox_output_file = args.output or os.path.splitext(args.pdf_file)[0] + '-bbox.json'
        DataProcessor.save_to_json(pdf.boxes, bbox_output_file)
        logging.info(f"Bounding boxes saved to '{bbox_output_file}'.")

def main():
    # Configure the argument parser
    parser = argparse.ArgumentParser(description='Extract text from PDF module fields specified in the configuration file and save the data to a JSON file.')
    subparsers = parser.add_subparsers(dest='command')

    # Evaluate subcommand
    evaluate_parser = subparsers.add_parser('evaluate', help="Save all bounding boxes read from the PDF file with their text and position.")
    evaluate_parser.add_argument('pdf_file', type=str, help='Path to the PDF file to analyze')
    evaluate_parser.add_argument('-O', '--output', type=str, help='Path to the output JSON file (default: same name as input file with .json extension)')

    # Read subcommand
    read_parser = subparsers.add_parser('read', help="Extract text from PDF module fields specified in the configuration file and save the data to a JSON file.")
    read_parser.add_argument('pdf_file', type=str, help='Path to the PDF file to analyze')
    read_parser.add_argument('-C', '--config', type=str, help='Path to the configuration file (.conf)', required=True)
    read_parser.add_argument('-O', '--output', type=str, help='Path to the output JSON file (default: same name as input file with .json extension)')
    read_parser.add_argument('-K', '--keyname', type=str, help='keyname in rowdict', default="Codice")
    read_parser.add_argument('--bbox', action='store_true', help='Always save bounding boxes even during the read operation (command "read")')
    read_parser.add_argument('--no-refile', action='store_true', help='Do not refile results')

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Parse arguments from the command line
    args = parser.parse_args()

    import locale

    # Imposta la nuova locale
    nuova_locale = 'it_IT.UTF-8'  # Ad esempio, impostiamo l'italiano come lingua
    locale.setlocale(locale.LC_ALL, nuova_locale)

    # Controlla se la locale è stata impostata correttamente
    locale_attuale = locale.getlocale()
    print("Locale attuale:", locale_attuale)
    
    # Execute the appropriate command
    if args.command == 'evaluate':
        evaluate_command(args)
    elif args.command == 'read':
        read_command(args)
    else:
        logging.error("Error: Invalid command. Use 'evaluate' to save all bounding boxes read from the PDF file with their text and position, or 'read' to extract text from PDF module fields specified in the configuration file and save the data to a JSON file.")

if __name__ == "__main__":
    main()
