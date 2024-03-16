# e-pdf-form-reader

The **e-pdf-form-reader** is a Python package designed to streamline the extraction of data from PDF files. It offers a straightforward and efficient solution for parsing PDF files containing forms, extracting form fields alongside their values, and structuring them for easy access and manipulation.

## Features

- **PDF Form Extraction:** Extracts form fields and their corresponding values from PDF files.
- **Structured Data:** Organizes extracted form data into a structured format for convenient handling.
- **Command-Line Interface (CLI):** Provides a CLI for seamless integration into workflows.
- **Cross-Platform Compatibility:** Compatible with Windows, macOS, and Linux.
- **Dependency Management:** Automatically installs required dependencies for smooth operation.

## Installation

You can install the **e-pdf-form-reader** package via pip:

```bash
pip install e-pdf-form-reader
```

## Usage

To utilize the package, import the necessary modules and leverage the provided functions for reading PDF forms. Below is a basic example:

```python
from e_pdf_form_reader import PDFFormReader

# Create an instance of PDFFormReader
pdf_reader = PDFFormReader('example_form.pdf')

# Extract form fields and values
form_data = pdf_reader.extract_form_data()

# Print the extracted data
print(form_data)
```

## Command-Line Interface (CLI)

The `pdf-form` command-line interface (CLI) allows you to extract text fields from PDF files according to a specified configuration. Here's how to use it:

### pdf-form Command-Line Interface (CLI) Manual

The `pdf-form` command-line interface (CLI) allows you to extract text from PDF module fields specified in a configuration file and save the data to a JSON file.

#### Installation

Ensure you have Python installed on your system. You can install the `pdf-form` CLI using pip:

```bash
pip install e-pdf-form-reader
```

#### Usage

To use the `pdf-form` CLI, execute the following command in your terminal:

```bash
pdf-form [COMMAND] [OPTIONS]
```

Replace `[COMMAND]` with one of the following commands:
- `evaluate`: Save all bounding boxes read from the PDF file with their text and position.
- `read`: Extract text from PDF module fields specified in the configuration file and save the data to a JSON file.

#### Options

- `-h, --help`: Show the help message and exit.
- `-v, --version`: Show the version number and exit.

#### Command: evaluate

Save all bounding boxes read from the PDF file with their text and position.

```bash
pdf-form evaluate [OPTIONS] pdf_file
```

- `pdf_file`: Path to the PDF file to analyze.

Options:
- `-O, --output`: Path to the output JSON file (default: same name as input file with .json extension).

#### Command: read

Extract text from PDF module fields specified in the configuration file and save the data to a JSON file.

```bash
pdf-form read [OPTIONS] pdf_file -C config
```

- `pdf_file`: Path to the PDF file to analyze.
- `-C, --config`: Path to the configuration file (.conf) (required).

Options:
- `-O, --output`: Path to the output JSON file (default: same name as input file with .json extension).
- `-K, --keyname`: Keyname in rowdict (default: "Codice").
- `--bbox`: Always save bounding boxes even during the read operation (command "read").
- `--no-refile`: Do not refile results.

#### Example

Here's an example of how to use the `pdf-form` CLI:

```bash
pdf-form read sample.pdf -C config.conf
```

This command will extract text from the PDF file "sample.pdf" according to the configuration specified in "config.conf" and save the data to a JSON file.

#### Note

If you encounter any issues or need further assistance, please refer to the project documentation or contact the maintainers.

For comprehensive usage instructions and examples, please consult the [documentation](https://github.com/exedre/e-pdf-form-reader).

## Contributing

Contributions are welcome! If you encounter issues, have feature requests, or wish to contribute, feel free to open an issue or submit a pull request on [GitHub](https://github.com/exedre/e-pdf-form-reader).

## License

This project is licensed under the MIT License. Refer to the [LICENSE](https://github.com/exedre/e-pdf-form-reader/blob/main/LICENSE) file for more details.



