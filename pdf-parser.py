#!/usr/bin/env python3

import fitz  # PyMuPDF
import pandas as pd
import argparse
import sys

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def parse_schedule_text(text):
    # Croatian day names and their corresponding abbreviations, including Saturday
    day_map = {
        'Ponedjeljak': 'MO',
        'Utorak': 'TU',
        'Srijeda': 'WE',
        'Četvrtak': 'TH',
        'Petak': 'FR',
        'Subota': 'SA',
    }

    # Split the extracted text by newlines
    lines = text.split('\n')

    schedule = []
    current_day = None
    slot = None

    for line in lines:
        line = line.strip()
        
        if line in day_map:
            # Found a day, update the current day
            current_day = day_map[line]
            slot = None  # Reset slot to None at the start of a new day
        elif line.endswith('.') and line[:-1].isdigit():
            # Found a slot number, update slot
            slot = int(line[:-1])
        elif current_day and slot is not None and line:
            # If there is a current day, slot, and class information
            schedule.append([current_day, line, slot])
        elif current_day and not line:
            # If the line is empty but we have a current day, continue to next line
            continue

    return schedule

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Parse a school schedule from a PDF file.")
    parser.add_argument("pdf_path", help="Path to the source PDF file")
    parser.add_argument("-o", "--output", help="Path to the output CSV file (default: stdout)", default=None)
    args = parser.parse_args()

    # Extract text from the PDF
    text = extract_text_from_pdf(args.pdf_path)

    # Parse the extracted text to get the schedule
    schedule = parse_schedule_text(text)

    # Check if any data was found
    if not schedule:
        print("No schedule data found. Please check the PDF file content or format.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(schedule, columns=['Day', 'Class', 'Slot'])

    # Write to output
    if args.output:
        df.to_csv(args.output, index=False, header=False)
    else:
        df.to_csv(sys.stdout, index=False, header=False)

if __name__ == "__main__":
    main()
