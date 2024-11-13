import json
import yaml
import argparse
import os

def convert_txt_to_format(input_file: str, output_file: str, format_type: str):
    """
    Converts a structured .txt file to a JSON or YAML file.

    :param input_file: Path to the input .txt file.
    :param output_file: Path where the output file will be saved.
    :param format_type: Desired output format ('json' or 'yaml').
    """
    # Read the input .txt file with ISO-8859-1 encoding to handle accents
    with open(input_file, 'r', encoding='ISO-8859-1') as f:
        lines = [line.strip().split('\t') for line in f.readlines()]

    # Extract headers and data rows
    headers = lines[0]
    data = [dict(zip(headers, row)) for row in lines[1:]]

    # Write the data to the specified format
    with open(output_file, 'w', encoding='utf-8') as f:
        if format_type.lower() == 'json':
            json.dump(data, f, indent=4, ensure_ascii=False)  # ensure_ascii=False preserves accents
        elif format_type.lower() == 'yaml':
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)  # allow_unicode preserves accents
        else:
            raise ValueError("Invalid format type. Choose 'json' or 'yaml'.")

def main():
    # Set up argument parsing for command line execution
    parser = argparse.ArgumentParser(description="Convert a structured .txt file to JSON or YAML.")
    parser.add_argument("input_file", help="Path to the input .txt file")
    parser.add_argument("output_file", help="Path where the output file will be saved")
    parser.add_argument("format_type", choices=["json", "yaml"], help="Desired output format (json or yaml)")

    # Parse arguments
    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: The file {args.input_file} does not exist.")
        return

    # Call the conversion function with parsed arguments
    try:
        convert_txt_to_format(args.input_file, args.output_file, args.format_type)
        print(f"File successfully converted to {args.format_type.upper()} format and saved as {args.output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Ensure the script only runs if executed directly
if __name__ == "__main__":
    main()

#TO RUN: python txt_to_format.py input.txt output.json json
#TO RUN: python txt_to_format.py input.txt output.yaml yaml