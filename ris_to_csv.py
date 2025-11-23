# ris_to_csv.py

import rispy
import pandas as pd
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Convert RIS files to CSV/Excel')
    parser.add_argument('--input', '-i', default='ris', help='Input folder containing .ris files (default: ris)')
    parser.add_argument('--output', '-o', default='output', help='Output folder (default: output)')
    parser.add_argument('--filename', '-f', default='exported', help='Output filename without extension (default: exported)')
    parser.add_argument('--format', '-t', choices=['csv', 'xlsx', 'both'], default='csv', 
                        help='Output format: csv, xlsx, or both (default: csv)')
    
    args = parser.parse_args()
    
    # Setup paths
    input_folder = Path(args.input)
    output_folder = Path(args.output)
    output_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all .ris files
    ris_files = list(input_folder.glob('*.ris'))
    
    if not ris_files:
        print(f"No .ris files found in {input_folder}")
        return
    
    print(f"Found {len(ris_files)} .ris file(s)")
    
    # Collect all entries
    all_entries = []
    for ris_file in ris_files:
        print(f"Processing {ris_file.name}...")
        with open(ris_file, 'r', encoding='utf-8') as f:
            entries = rispy.load(f)
            all_entries.extend(entries)
    
    print(f"Total entries: {len(all_entries)}")
    
    # Create DataFrame
    df = pd.DataFrame(all_entries)
    
    # Export based on format
    if args.format in ['csv', 'both']:
        csv_path = output_folder / f"{args.filename}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Exported to {csv_path}")
    
    if args.format in ['xlsx', 'both']:
        xlsx_path = output_folder / f"{args.filename}.xlsx"
        df.to_excel(xlsx_path, index=False)
        print(f"Exported to {xlsx_path}")

if __name__ == "__main__":
    main()
