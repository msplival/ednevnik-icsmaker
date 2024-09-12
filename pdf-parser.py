#!/usr/bin/env python3

import pdfplumber
import pandas as pd
import argparse
import sys

def extract_table_from_pdf(pdf_path):
    # Open the PDF file using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]  # Assuming the table is on the first page
        table = first_page.extract_table()  # Extract the table
    return table

def parse_schedule_table(table):
    # Croatian day names and their corresponding abbreviations
    day_map = {
        'Ponedjeljak': 'MO',
        'Utorak': 'TU',
        'Srijeda': 'WE',
        'Četvrtak': 'TH',
        'Petak': 'FR',
        'Subota': 'SA',
    }

    # Extract the headers (days) and the rest of the rows
    headers = table[0]
    rows = table[1:]

    # Prepare schedule list
    schedule = []

    # Process each row
    for row in rows:
        slot = row[0].strip('.')  # Extract the slot number and remove the trailing '.'
        for i, cell in enumerate(row[1:], 1):  # Start from 1 to skip the slot column
            day = headers[i]
            if day in day_map and cell.strip():  # Check if the day is valid and the cell is not empty
                schedule.append([day_map[day], cell.strip(), slot])

    return schedule

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Parse a school schedule from a PDF file.")
    parser.add_argument("pdf_path", help="Path to the source PDF file")
    parser.add_argument("-o", "--output", help="Path to the output CSV file (default: stdout)", default=None)
    args = parser.parse_args()

    # Extract the table from the PDF
    table = extract_table_from_pdf(args.pdf_path)

    # Parse the extracted table to get the schedule
    schedule = parse_schedule_table(table)

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
