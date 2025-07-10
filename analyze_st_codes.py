#!/usr/bin/env python
import pdfplumber
import re
import csv
import os
import warnings
import logging
from collections import defaultdict, Counter

# Suppress pdfminer warnings
logging.getLogger('pdfminer').setLevel(logging.ERROR)

def analyze_st_pdf(pdf_path, output_dir="./output"):
    """
    Analyze a PDF file containing ST codes for format consistency.
    Count codes per page and identify patterns.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize counters and data structures
    total_st_codes = 0
    unique_st_codes = set()
    page_counts = []
    st_types = {}
    format_issues = []
    pages_with_codes = 0
    
    # Full text content for later analysis
    full_text = ""
    
    print(f"Analyzing PDF: {pdf_path}")
    
    # Open PDF and process page by page
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages in PDF: {len(pdf.pages)}")
        
        # Process each page
        for i, page in enumerate(pdf.pages):
            try:
                # Extract text from page
                page_text = page.extract_text()
                full_text += page_text + "\n\n"
                
                # Count ST codes on this page
                # Pattern: ST followed by numbers at start of line
                st_pattern = re.compile(r'^(ST\d+)\s+([^\n]+?)(?:\s+UID:|$)', re.MULTILINE)
                matches = st_pattern.findall(page_text)
                
                # Get types if available
                type_pattern = re.compile(r'(ST\d+).*?Type:\s+(\w+)', re.DOTALL)
                type_matches = type_pattern.findall(page_text)
                
                page_st_codes = set([m[0] for m in matches])
                num_codes = len(page_st_codes)
                
                # Track all page counts
                page_counts.append((i+1, num_codes, sorted(list(page_st_codes))))
                
                # Collect type information
                for code, type_code in type_matches:
                    if code in st_types and st_types[code] != type_code:
                        format_issues.append(f"Inconsistent type for {code}: {st_types[code]} vs {type_code} on page {i+1}")
                    st_types[code] = type_code
                
                # Add to totals
                total_st_codes += num_codes
                unique_st_codes.update(page_st_codes)
                if num_codes > 0:
                    pages_with_codes += 1
                
                # Check for format issues
                for code, desc in matches:
                    if not desc.strip():
                        format_issues.append(f"Missing description for {code} on page {i+1}")
                    if "Type:" not in page_text:
                        format_issues.append(f"Missing Type field for codes on page {i+1}")
                
                if i % 10 == 0:
                    print(f"Processed {i+1}/{len(pdf.pages)} pages")
                    
            except Exception as e:
                format_issues.append(f"Error processing page {i+1}: {str(e)}")
    
    # Save full text for reference
    with open(os.path.join(output_dir, "st_extracted_full_text.txt"), "w", encoding="utf-8") as f:
        f.write(full_text)
    
    # Analyze codes without type information
    codes_without_type = [code for code in unique_st_codes if code not in st_types]
    
    # Save page counts to CSV
    with open(os.path.join(output_dir, "st_counts_by_page.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Page", "Number of ST Codes", "Codes"])
        for page, count, codes in page_counts:
            writer.writerow([page, count, ", ".join(codes)])
    
    # Calculate distribution statistics
    code_counts = [count for _, count, _ in page_counts]
    if code_counts:
        avg_codes_per_page = sum(code_counts) / len(code_counts)
        most_common_count = Counter(code_counts).most_common(1)[0][0]
    else:
        avg_codes_per_page = 0
        most_common_count = 0
    
    # Types distribution
    type_distribution = Counter(st_types.values())
    
    # Print summary
    print("\nAnalysis Complete!")
    print(f"Total ST codes found: {total_st_codes}")
    print(f"Unique ST codes found: {len(unique_st_codes)}")
    print(f"Pages with ST codes: {pages_with_codes} / {len(pdf.pages)}")
    print(f"Average ST codes per page with codes: {avg_codes_per_page:.2f}")
    print(f"Most common number of codes per page: {most_common_count}")
    print(f"Number of different code types: {len(type_distribution)}")
    print("\nType distribution:")
    for type_code, count in type_distribution.most_common(10):
        print(f"  {type_code}: {count} codes")
    
    print("\nFormat consistency:")
    if format_issues:
        print(f"Found {len(format_issues)} potential format issues:")
        for i, issue in enumerate(format_issues[:10]):
            print(f"  - {issue}")
        if len(format_issues) > 10:
            print(f"  ... and {len(format_issues) - 10} more issues")
    else:
        print("No format issues detected!")
    
    if codes_without_type:
        print(f"\nFound {len(codes_without_type)} codes without type information")
        print(f"Examples: {', '.join(sorted(codes_without_type)[:5])}")
    
    # Return summary data
    return {
        "total_st_codes": total_st_codes,
        "unique_st_codes": len(unique_st_codes),
        "pages_with_codes": pages_with_codes,
        "avg_codes_per_page": avg_codes_per_page,
        "most_common_count": most_common_count,
        "type_distribution": type_distribution,
        "format_issues": format_issues,
        "codes_without_type": codes_without_type
    }

if __name__ == "__main__":
    analyze_st_pdf("./pdfs/tabular_only_ST.pdf")
