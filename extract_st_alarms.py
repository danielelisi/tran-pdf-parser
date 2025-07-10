#!/usr/bin/env python
import argparse
import pdfplumber
import re
import csv
import os
import logging
import warnings
from collections import Counter

# Suppress pdfminer warnings
logging.getLogger('pdfminer').setLevel(logging.ERROR)

def extract_full_text(pdf_path):
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        String containing all extracted text
    """
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text += page.extract_text() + "\n\n"
    return full_text

def count_st_codes(text):
    """
    Count the total number of ST codes in the text.
    
    Args:
        text: The text to search for ST codes
        
    Returns:
        dict: Statistics about ST codes found
    """
    # Find all ST codes at start of lines
    st_pattern = re.compile(r'^(ST\d+)\s+([^\n]+?)(?:\s+UID:|$)', re.MULTILINE)
    matches = st_pattern.findall(text)
    
    # Count unique ST codes
    unique_codes = set([code for code, _ in matches])
    
    # Find codes with Type field
    type_pattern = re.compile(r'(ST\d+).*?Type:\s+(\w+)', re.DOTALL)
    type_matches = type_pattern.findall(text)
    
    # Count types
    type_counts = Counter([type_code for _, type_code in type_matches])
    
    return {
        "total": len(matches),
        "unique": len(unique_codes),
        "with_type": len(type_matches),
        "unique_with_type": len(set([code for code, _ in type_matches])),
        "type_distribution": type_counts,
        "codes": sorted(list(unique_codes)[:20])  # Limit to first 20 for display
    }

def extract_st_alarms(pdf_path):
    """
    Extract ST alarm records from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        List of dictionaries containing alarm data: SerialID, Type
        where SerialID combines the ST code and alert name
    """
    alarms = []
    
    # Extract full text from PDF
    full_text = extract_full_text(pdf_path)
    
    # Find all ST code blocks
    st_pattern = re.compile(r'(ST\d+)\s+([^\n]+?)(?:\s+UID:|$)', re.MULTILINE)
    st_matches = list(st_pattern.finditer(full_text))
    
    for i, match in enumerate(st_matches):
        code = match.group(1)
        initial_name = match.group(2).strip()
        start_pos = match.start()
        
        # Determine end position (start of next ST code or end of text)
        end_pos = len(full_text) if i == len(st_matches) - 1 else st_matches[i+1].start()
        block_text = full_text[start_pos:end_pos]
        
        # Join ST code and alert name for SerialID
        serial_id = f"{code} {initial_name}"
        
        # Extract Type field
        type_match = re.search(r'Type:\s+(\w+)', block_text)
        if type_match:
            type_code = type_match.group(1)
            
            alarms.append({
                "SerialID": serial_id,
                "Type": type_code
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
    fieldnames = ["SerialID", "Type"]
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for alarm in alarms:
            writer.writerow(alarm)

def write_text_to_file(text, file_path):
    """
    Write text content to a file.
    
    Args:
        text: Text content to write
        file_path: Path to the output file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode="w", encoding="utf-8") as f:
        f.write(text)

def main():
    parser = argparse.ArgumentParser(
        description="Extract ST alarm records from a PDF and export to CSV"
    )
    parser.add_argument("pdf", help="Path to the input PDF file")
    parser.add_argument("-o", "--output", dest="csv", default="./output/st_alerts.csv", help="Path for the output CSV file")
    args = parser.parse_args()

    try:
        # Make sure output directory exists
        os.makedirs(os.path.dirname(args.csv), exist_ok=True)
        
        # Extract and save full text for debugging
        full_text = extract_full_text(args.pdf)
        write_text_to_file(full_text, "./output/st_extracted_full_text.txt")
        
        # Extract and save alarms
        alarms = extract_st_alarms(args.pdf)
        write_alarms_to_csv(alarms, args.csv)

        # Count ST codes and display statistics
        st_stats = count_st_codes(full_text)
        print(f"\nST Code Statistics:")
        print(f"  Total ST code occurrences: {st_stats['total']}")
        print(f"  Unique ST codes: {st_stats['unique']}")
        print(f"  ST entries with type field: {st_stats['with_type']}")
        print(f"  Unique ST codes with type: {st_stats['unique_with_type']}")
        print(f"\n  Type distribution:")
        for type_code, count in st_stats['type_distribution'].most_common():
            print(f"    - {type_code}: {count}")
        
        print(f"\n  First 20 codes: {', '.join(st_stats['codes'])}" + 
              ("..." if len(st_stats['codes']) > 20 else ""))
        
        # Verification
        print(f"\nExtracted {len(alarms)} ST alarm records to {args.csv}")
        
        # Check extraction completeness
        if len(alarms) == st_stats['unique_with_type']:
            print(f"✅ Verification successful: Extracted all {len(alarms)} ST codes with type information")
        else:
            print(f"⚠️ Verification issue: Found {st_stats['unique_with_type']} ST codes with type, but extracted {len(alarms)}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
