#!/usr/bin/env python3

import re
import os

# Path to files
input_file = "output/extracted_full_text.txt"
analysis_output = "output/fm_codes_analysis.txt"

def main():
    # Read the full text file
    with open(input_file, 'r', encoding='utf-8') as f:
        full_text = f.read()
    
    # Different patterns to find FM codes
    basic_pattern = re.compile(r'FM\d+')
    line_start_pattern = re.compile(r'^FM\d+', re.MULTILINE)
    uid_pattern = re.compile(r'(FM\d+)\s+[^\n]+?UID:', re.MULTILINE)
    full_alarm_pattern = re.compile(
        r"(FM\d+)\s+([^\n]+?)\s+UID:[^\n]+\s+ResetLevel:[^\n]+\s+DeacLevel:[^\n]+.*?Properties.*?Red\. Avail\.:\s+(yes|no).*?Brake-Prog\.:\s+(\d)",
        re.DOTALL | re.IGNORECASE
    )
    
    # Find all matches
    all_matches = basic_pattern.findall(full_text)
    line_start_matches = line_start_pattern.findall(full_text)
    uid_matches = uid_pattern.findall(full_text)
    full_alarm_matches = [match.group(1) for match in full_alarm_pattern.finditer(full_text)]
    
    # Convert to sets for comparison
    all_set = set(all_matches)
    line_start_set = set(line_start_matches)
    uid_set = set(uid_matches)
    full_alarm_set = set(full_alarm_matches)
    
    # Find differences
    in_all_not_uid = all_set - uid_set
    in_uid_not_full = uid_set - full_alarm_set
    
    # Total counts
    total_fm_mentions = len(all_matches)
    unique_fm_mentions = len(all_set)
    line_start_count = len(line_start_matches)
    uid_count = len(uid_matches)
    full_alarm_count = len(full_alarm_matches)
    
    # Write analysis to file
    with open(analysis_output, 'w', encoding='utf-8') as f:
        f.write(f"FM Code Analysis\n")
        f.write(f"==============\n\n")
        f.write(f"Total FM mentions: {total_fm_mentions}\n")
        f.write(f"Unique FM codes: {unique_fm_mentions}\n")
        f.write(f"FM codes at line start: {line_start_count}\n")
        f.write(f"FM codes with UID: {uid_count}\n")
        f.write(f"FM codes with full alarm structure: {full_alarm_count}\n\n")
        
        f.write(f"FM codes found in text but not with UID ({len(in_all_not_uid)}):\n")
        for code in sorted(in_all_not_uid):
            # Find the context around this code
            pattern = re.compile(r'.{0,50}' + re.escape(code) + r'.{0,50}', re.DOTALL)
            contexts = pattern.findall(full_text)
            for context in contexts[:1]:  # Limit to first occurrence
                f.write(f"  {code}: {context.replace(code, f'>>>{code}<<<')}\n")
        
        f.write(f"\nFM codes with UID but not extractable as full alarms ({len(in_uid_not_full)}):\n")
        for code in sorted(in_uid_not_full):
            # Find the block containing this code
            block_start = full_text.find(code)
            if block_start >= 0:
                block_end = min(block_start + 500, len(full_text))
                block = full_text[block_start:block_end]
                f.write(f"  {code}: {block[:200].replace(code, f'>>>{code}<<<')}...\n")
        
        # Find expected 1273 codes vs what we found
        f.write(f"\nExpected vs Found:\n")
        f.write(f"  Expected: 1273 unique FM codes\n")
        f.write(f"  Found with UID: {uid_count}\n")
        f.write(f"  Missing: {1273 - uid_count} codes\n")
    
    print(f"Analysis complete. Results saved to {analysis_output}")
    print(f"\nSummary:")
    print(f"  Total FM mentions in text: {total_fm_mentions}")
    print(f"  Unique FM codes: {unique_fm_mentions}")
    print(f"  FM codes with UID: {uid_count}")
    print(f"  FM codes with full alarm structure: {full_alarm_count}")
    print(f"  Expected: 1273 | Found: {uid_count} | Difference: {1273 - uid_count}")

if __name__ == "__main__":
    main()
