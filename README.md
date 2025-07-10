# PDF Alarm Extractor

A Python tool to extract alarm records from PDF files containing structured alarm blocks. The tool identifies FM serial codes, alert names, and properties such as BrakeProg and RedAvail values from complex PDF documents.

## Features

- Extract alarm records with FM codes and properties from PDFs
- Join FM code and alert name in a single SerialID field for easier reference
- Count and analyze FM code occurrences per page
- Export results to CSV format
- Detailed statistics on extracted codes
- Suppress irrelevant warnings

## Requirements

- Python 3.6+
- pdfplumber library

## Installation

1. Clone this repository or download the source code

2. Create and activate a virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/Mac
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Main Extraction Script

Extract alarm records from a PDF and save to CSV:

```bash
python main.py "your_pdf_file.pdf" [-o output_file.csv]
```

- If no output file is specified, results will be saved to `./output/alerts.csv`
- The script will also save the full extracted text to `./output/extracted_full_text.txt` for debugging

### FM Code Analysis Tools

#### Count FM Codes by Page

Count FM code occurrences on each page of the PDF:

```bash
python count_fm_by_page.py "your_pdf_file.pdf" [-o output_file.csv]
```

This will generate:
- A CSV file with per-page counts
- A distribution CSV showing which pages each FM code appears on

#### Filter FM Codes

Extract only lines containing valid FM codes:

```bash
python filter_fm_codes.py
```

This analyzes `output/extracted_full_text.txt` and saves lines with FM codes to `output/fm_lines_only.txt`.

#### Analyze FM Codes

Perform detailed analysis of FM code patterns:

```bash
python analyze_fm_codes.py
```

This analyzes the extracted text file and provides statistics on FM code occurrences, unique codes, and more.

#### Count Unique FM Codes

Count and list unique FM codes:

```bash
python count_unique_fm_codes.py
```

Creates a CSV file with each unique FM code and its occurrence count.

## Output Format

The main extraction script produces a CSV file with the following columns:

- **SerialID**: Combined FM code and alert name (e.g., "FM123 Alert Description")
- **BrakeProg**: The Brake-Prog value (integer)
- **RedAvail**: The Red. Avail value (yes/no)

## Troubleshooting

- If you encounter extraction issues, check the `extracted_full_text.txt` file to see if the PDF was properly parsed
- For PDFs with unusual formatting, you may need to adjust the regex patterns in the `extract_alarms` function
