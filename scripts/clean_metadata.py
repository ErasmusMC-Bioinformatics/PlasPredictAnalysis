#!/usr/bin/env python3

import os

def clean_metadata_file(input_file: str, output_file: str):
    """
    Filters a file to keep only the lines that have exactly 5 fields,
    separated by a pipe ('|').

    Args:
        input_file: The path to the input file.
        output_file: The path to the output file where the cleaned data will be saved.
    """
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"Error: The input file '{input_file}' was not found.")
        return

    try:
        # Open the input and output files
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            cleaned_lines_count = 0
            
            # Read the file line by line
            for line in infile:
                # Strip leading/trailing whitespace and split the line by the pipe character
                fields = line.strip().split('|')
                
                # Check if the number of fields is exactly 5
                if len(fields) == 5:
                    outfile.write(line)
                    cleaned_lines_count += 1
        
        print(f"Successfully cleaned the file. Retained {cleaned_lines_count} valid lines.")
        print(f"The cleaned data has been saved to '{output_file}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_file_name = "metadata.txt"
    output_file_name = "metadata_clean.txt"
    clean_metadata_file(input_file_name, output_file_name)
