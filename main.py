#!/usr/bin/env python3
"""
Script: extract_alarms.py

Loads a PDF, scans for alarm blocks starting with codes FM\\d{1,3}, extracts fields, and writes results to CSV.
Usage:
    python extract_alarms.py "Alarm List Akmene Wind Farm SCADA (2).pdf" output.csv
"""

import pdfplumber
import re
import csv
import argparse
import logging
import warnings
import os

# Suppress pdfminer warnings about CropBox
logging.getLogger('pdfminer').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning, message='.*CropBox missing.*')

def extract_full_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            full_text.append(text)
        return "\n".join(full_text)

def count_fm_codes(text):
    """
    Count the total number of FM codes (serial numbers) in the text.
    
    Args:
        text: The text to search for FM codes
        
    Returns:
        dict: Statistics about FM codes found
    """
    # Find all occurrences of FM followed by numbers that are likely actual alarm codes
    # This pattern looks for lines that start with FM followed by numbers
    fm_pattern = re.compile(r'^(FM\d+)\s+', re.MULTILINE)
    matches = fm_pattern.findall(text)
    
    # Count unique FM codes
    unique_codes = set(matches)
    
    # Find alarm blocks with properties (more accurate count of valid alarms)
    block_pattern = re.compile(r'^(FM\d+)\s+([A-Z][^\n]+?)\s+UID:', re.MULTILINE)
    block_matches = block_pattern.findall(text)
    unique_blocks = set([code for code, _ in block_matches])
    
    return {
        "total": len(matches),
        "unique": len(unique_codes),
        "valid_alarms": len(block_matches),
        "unique_valid": len(unique_blocks),
        "codes": sorted(list(unique_codes)[:20])  # Limit to first 20 for display
    }

def extract_alarms(pdf_path):
    """
    Extract alarm records from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries containing alarm data: SerialID, BrakeProg, RedAvail
        where SerialID combines the FM code and alert name
    """
    alarms = []
    
    # Extract full text from PDF
    full_text = extract_full_text(pdf_path)
    
    # First, find all FM code blocks
    fm_pattern = re.compile(r'(FM\d+)\s+([^\n]+)\s+UID:', re.MULTILINE)
    fm_matches = list(fm_pattern.finditer(full_text))
    
    for i, match in enumerate(fm_matches):
        code = match.group(1)
        initial_name = match.group(2).strip()
        start_pos = match.start()
        
        # Determine end position (start of next FM code or end of text)
        end_pos = len(full_text) if i == len(fm_matches) - 1 else fm_matches[i+1].start()
        block_text = full_text[start_pos:end_pos]
        
        # Extract complete alert name (including continuation lines)
        # Look for text between the UID line and the Properties line
        uid_to_properties = re.search(r'UID:[^\n]+\s+ResetLevel:[^\n]+\s+DeacLevel:\s*\d+\s*\n([\s\S]*?)\n[^\n]*Properties', block_text)
        
        # Initialize full alert name with first line
        full_alert_name = initial_name
        
        # If continuation text exists between UID and Properties that doesn't look like document header
        if uid_to_properties:
            continuation = uid_to_properties.group(1).strip()
            # Check if this is actually alert name continuation (not description or document header)
            if continuation and not re.search(r'Page:|Rev:|Doc:|WT CTRL|\d+\s*/\s*\d+', continuation):
                # Add continuation text if it appears to be part of the alert name
                if len(continuation.split()) <= 10 and not continuation.startswith('The '):
                    full_alert_name += ' ' + continuation
        
        # Extract other required fields
        properties_match = re.search(r'Properties.*?Red\. Avail\.:\s+(yes|no).*?Brake-Prog\.:\s+(\d)', block_text, re.DOTALL | re.IGNORECASE)
        
        if properties_match:
            # Normalize whitespace in alert name
            full_alert_name = re.sub(r"\s+", " ", full_alert_name).strip()
            
            # Join FM code and alert name for SerialID
            serial_id = f"{code} {full_alert_name}"
            red_avail = properties_match.group(1).lower()
            brake_prog = int(properties_match.group(2))
            
            alarms.append({
                "SerialID": serial_id,
                "BrakeProg": brake_prog,
                "RedAvail": red_avail
            })
    
    return alarms


def write_alarms_to_csv(alarms, csv_path):
    """
    Write extracted alarm records to a CSV file.
    
    Args:
        alarms: List of dictionaries containing alarm data
        csv_path: Path to the output CSV file
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Write to CSV
    fieldnames = ["SerialID", "BrakeProg", "RedAvail"]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for alarm in alarms:
            writer.writerow(alarm)

def write_text_to_file(text, file_path):
    """
    Write text content to a file.
    
    Args:
        text: String content to write
        file_path: Path to the output file
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser(
        description="Extract alarm blocks from a PDF and export to CSV"
    )
    parser.add_argument("pdf", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", dest="csv", default="./output/alerts.csv", help="Path for the output CSV file")
    args = parser.parse_args()

    try:
        # Make sure output directory exists
        os.makedirs(os.path.dirname(args.csv), exist_ok=True)
        
        # Extract and save full text for debugging
        full_text = extract_full_text(args.pdf)
        write_text_to_file(full_text, "./output/extracted_full_text.txt")
        
        # Extract and save alarms
        alarms = extract_alarms(args.pdf)
        write_alarms_to_csv(alarms, args.csv)

        # Count FM codes and display statistics
        fm_stats = count_fm_codes(full_text)
        print(f"\nFM Code Statistics:")
        print(f"  Total FM code occurrences: {fm_stats['total']}")
        print(f"  Unique FM codes: {fm_stats['unique']}")
        print(f"  Valid alarm entries: {fm_stats['valid_alarms']}")
        print(f"  Unique valid FM codes: {fm_stats['unique_valid']}")
        print(f"\n  First 20 codes: {', '.join(fm_stats['codes'])}" + 
              ("..." if len(fm_stats['codes']) > 20 else ""))
        
        # Verification against expected count
        if fm_stats['unique_valid'] == 1270:
            print(f"✅ Verification successful: Found 1270 unique valid alarm codes as expected")
        else:
            print(f"⚠️ Verification issue: Found {fm_stats['unique_valid']} alarm codes, expected 1270")
            
        print(f"\nExtracted {len(alarms)} alarm records to {args.csv}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
    return 0


if __name__ == "__main__":
    main()
