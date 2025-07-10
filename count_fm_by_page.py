#!/usr/bin/env python3

import pdfplumber
import re
import argparse
import csv
import os
import logging
import warnings
from collections import defaultdict

# Suppress pdfminer warnings about CropBox
logging.getLogger('pdfminer').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning)

def count_fm_codes_by_page(pdf_path, output_csv=None):
    """
    Count FM serial numbers on each page of a PDF file
    
    Args:
        pdf_path: Path to the PDF file
        output_csv: Path to save results as CSV (optional)
        
    Returns:
        Dictionary with page numbers as keys and counts as values
    """
    # Dictionary to store results
    results = {
        'by_page': defaultdict(int),          # Page number -> count of FM codes
        'by_page_unique': defaultdict(set),   # Page number -> set of unique FM codes
        'code_locations': defaultdict(list),  # FM code -> list of pages it appears on
        'totals': {
            'total_occurrences': 0,
            'unique_codes': set()
        }
    }
    
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        
        # Regular expression pattern for valid FM codes
        # Looking for FM followed by digits, followed by space and capital letter
        fm_pattern = re.compile(r'^(FM\d+)\s+([A-Z])', re.MULTILINE)
        
        # Process each page
        for i, page in enumerate(pdf.pages):
            # Extract text from the page
            try:
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                # Find all FM codes on this page
                matches = fm_pattern.findall(page_text)
                
                # Count occurrences
                page_number = i + 1
                fm_codes = [match[0] for match in matches]  # Extract just the FM code part
                
                # Update counts
                results['by_page'][page_number] = len(fm_codes)
                results['by_page_unique'][page_number].update(fm_codes)
                
                # Update code locations
                for code in fm_codes:
                    results['code_locations'][code].append(page_number)
                    
                # Update totals
                results['totals']['total_occurrences'] += len(fm_codes)
                results['totals']['unique_codes'].update(fm_codes)
                
                print(f"Page {page_number}/{total_pages}: Found {len(fm_codes)} FM codes, {len(results['by_page_unique'][page_number])} unique")
                
            except Exception as e:
                print(f"Error processing page {i+1}: {str(e)}")
    
    # Write results to CSV if output_csv is provided
    if output_csv:
        with open(output_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Page', 'Total FM Codes', 'Unique FM Codes'])
            
            # Sort by page number
            for page in sorted(results['by_page'].keys()):
                writer.writerow([
                    page, 
                    results['by_page'][page],
                    len(results['by_page_unique'][page])
                ])
            
            # Add a summary row
            writer.writerow([''])
            writer.writerow([
                'Total', 
                results['totals']['total_occurrences'],
                len(results['totals']['unique_codes'])
            ])
        
        print(f"Results saved to {output_csv}")
        
        # Also save code distribution to a separate CSV
        dist_csv = os.path.splitext(output_csv)[0] + '_distribution.csv'
        with open(dist_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['FM Code', 'Pages Found On', 'Occurrences'])
            
            # Sort by FM code
            for code in sorted(results['code_locations'].keys()):
                pages = results['code_locations'][code]
                writer.writerow([
                    code,
                    ', '.join(map(str, pages)),
                    len(pages)
                ])
                
        print(f"FM code distribution saved to {dist_csv}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total FM code occurrences: {results['totals']['total_occurrences']}")
    print(f"Unique FM codes: {len(results['totals']['unique_codes'])}")
    print(f"Pages with FM codes: {len(results['by_page'])}")
    
    # Find pages with most codes
    top_pages = sorted(results['by_page'].items(), key=lambda x: x[1], reverse=True)[:5]
    print("\nPages with most FM codes:")
    for page, count in top_pages:
        print(f"  Page {page}: {count} codes")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="Count FM serial numbers on each page of a PDF file"
    )
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("-o", "--output", dest="csv", 
                       default="./output/fm_counts_by_page.csv",
                       help="Path for the output CSV file")
    args = parser.parse_args()
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.csv), exist_ok=True)
        
        # Count FM codes by page
        count_fm_codes_by_page(args.pdf, args.csv)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    main()
