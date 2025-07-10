#!/usr/bin/env python3

import re
import csv
from collections import Counter

def main():
    # Path to filtered FM lines file
    input_file = "output/fm_lines_only.txt"
    output_csv = "output/unique_fm_codes.csv"
    
    # Extract FM codes with a regex that captures just the FM number
    fm_pattern = re.compile(r'^(FM\d+)\s')
    fm_codes = []
    
    # Read lines and extract codes
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = fm_pattern.match(line)
            if match:
                fm_codes.append(match.group(1))
    
    # Count occurrences of each unique code
    code_counter = Counter(fm_codes)
    unique_codes = list(code_counter.keys())
    unique_codes.sort()
    
    # Write to CSV
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['FM Code', 'Occurrences'])
        for code in unique_codes:
            writer.writerow([code, code_counter[code]])
    
    # Print results
    print(f"Total FM code occurrences: {len(fm_codes)}")
    print(f"Unique FM codes found: {len(unique_codes)}")
    print(f"Expected unique FM codes: 1273")
    print(f"Difference: {len(unique_codes) - 1273}")
    print(f"Results saved to {output_csv}")
    
    # Print the first few and last few codes
    print("\nFirst 10 unique FM codes:")
    for code in unique_codes[:10]:
        print(f"  {code} ({code_counter[code]} occurrences)")
    
    print("\nLast 10 unique FM codes:")
    for code in unique_codes[-10:]:
        print(f"  {code} ({code_counter[code]} occurrences)")
    
    # Check for duplicates (codes appearing more than once)
    duplicates = [code for code, count in code_counter.items() if count > 1]
    if duplicates:
        print(f"\nFound {len(duplicates)} codes appearing multiple times:")
        for code in duplicates:
            print(f"  {code} appears {code_counter[code]} times")

if __name__ == "__main__":
    main()
