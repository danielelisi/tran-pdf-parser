#!/usr/bin/env python3

import re

# Path to input and output files
input_file = "output/extracted_full_text.txt"
output_file = "output/fm_lines_only.txt"

# Regular expression to match FM codes at the start of a line followed by a space and then a capital letter
fm_pattern = re.compile(r'^(FM\d+)\s+([A-Z])')

# Read the input file and filter lines
with open(input_file, 'r', encoding='utf-8') as infile:
    # Filter lines that start with FM codes followed by a space and a capital letter
    fm_lines = []
    for line in infile:
        match = fm_pattern.match(line)
        if match:
            fm_lines.append((match.group(1), line.strip()))

# Write to output file with format: FM_CODE,LINE_CONTENT
with open(output_file, 'w', encoding='utf-8') as outfile:
    for fm_code, line in fm_lines:
        outfile.write(f"{fm_code},{line}\n")

print(f"Filtered {len(fm_lines)} lines containing valid FM codes to {output_file}")

# Count unique FM codes
unique_fm_codes = set(code for code, _ in fm_lines)
print(f"Found {len(unique_fm_codes)} unique FM codes")
print(f"Expected: 1273 | Found: {len(unique_fm_codes)} | Difference: {len(unique_fm_codes) - 1273}")

# Exit here as we've already written to file
exit(0)


