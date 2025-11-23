import pandas as pd
import argparse
from pathlib import Path

def count_non_null(row):
    """Count non-null values in a row."""
    return row.notna().sum()

def merge_duplicate_sources(df, doi_column):
    """
    Create a mapping of DOI to merged Source_Database information.
    Returns a Series with DOI as index and merged sources as values.
    """
    if 'Source_Database' not in df.columns:
        return pd.Series(dtype=str)
    
    # Group by DOI and aggregate unique sources
    merged = df.groupby(doi_column)['Source_Database'].apply(
        lambda x: ', '.join(sorted(x.dropna().unique()))
    )
    return merged

def deduplicate_csv(input_file, output_file, keep_strategy='most_complete', 
                   merge_sources=True, doi_column='DOI'):
    """
    Remove duplicate records from a CSV file based on DOI.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        keep_strategy: Strategy for keeping records ('most_complete', 'first', 'last')
        merge_sources: If True, merge Source_Database info from duplicates
        doi_column: Name of the DOI column to use for deduplication
    """
    
    print(f"Loading {input_file}...")
    df = pd.read_csv(input_file)
    
    initial_count = len(df)
    print(f"Initial record count: {initial_count}")
    
    # Check if DOI column exists
    if doi_column not in df.columns:
        print(f"Error: Column '{doi_column}' not found in the CSV file.")
        print(f"Available columns: {', '.join(df.columns)}")
        return
    
    # Remove records without DOI
    records_without_doi = df[doi_column].isna().sum()
    if records_without_doi > 0:
        print(f"Warning: {records_without_doi} records have no DOI and cannot be checked for duplicates.")
    
    # Filter to only records with DOI
    df_with_doi = df[df[doi_column].notna()].copy()
    df_without_doi = df[df[doi_column].isna()].copy()
    
    # Find duplicates
    duplicate_mask = df_with_doi.duplicated(subset=[doi_column], keep=False)
    duplicate_count = duplicate_mask.sum()
    unique_duplicate_dois = df_with_doi[duplicate_mask][doi_column].nunique()
    
    print(f"\nDuplicate analysis:")
    print(f"  Records with duplicates: {duplicate_count}")
    print(f"  Unique DOIs with duplicates: {unique_duplicate_dois}")
    
    if duplicate_count == 0:
        print("\nNo duplicates found. Saving original file...")
        df.to_csv(output_file, index=False)
        print(f"Output saved to: {output_file}")
        return
    
    # Show duplicate examples
    if unique_duplicate_dois > 0:
        print("\nExample duplicates found:")
        duplicate_dois = df_with_doi[duplicate_mask][doi_column].unique()[:3]
        for doi in duplicate_dois:
            dups = df_with_doi[df_with_doi[doi_column] == doi]
            print(f"\n  DOI: {doi}")
            if 'Source_Database' in dups.columns:
                sources = dups['Source_Database'].tolist()
                print(f"    Found in: {', '.join(str(s) for s in sources)}")
            if 'Title' in dups.columns:
                title = dups['Title'].iloc[0]
                if pd.notna(title):
                    title_short = title[:60] + "..." if len(str(title)) > 60 else title
                    print(f"    Title: {title_short}")
    
    # Apply deduplication strategy
    print(f"\nApplying deduplication strategy: {keep_strategy}")
    
    if keep_strategy == 'most_complete':
        # Calculate completeness score for each record
        df_with_doi['_completeness_score'] = df_with_doi.apply(lambda row: count_non_null(row), axis=1)
        
        # Sort by DOI and completeness (descending)
        df_with_doi = df_with_doi.sort_values(
            [doi_column, '_completeness_score'], 
            ascending=[True, False]
        )
        
        # If merging sources, do it before dropping duplicates
        if merge_sources and 'Source_Database' in df_with_doi.columns:
            print("Merging source information from duplicates...")
            merged_sources = merge_duplicate_sources(df_with_doi, doi_column)
            # Keep first (most complete) record per DOI
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='first').copy()
            # Update Source_Database with merged info
            df_deduplicated['Source_Database'] = df_deduplicated[doi_column].map(merged_sources)
        else:
            # Just keep most complete
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='first').copy()
        
        # Remove helper column
        df_deduplicated = df_deduplicated.drop('_completeness_score', axis=1)
        
    elif keep_strategy == 'first':
        if merge_sources and 'Source_Database' in df_with_doi.columns:
            merged_sources = merge_duplicate_sources(df_with_doi, doi_column)
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='first').copy()
            df_deduplicated['Source_Database'] = df_deduplicated[doi_column].map(merged_sources)
        else:
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='first').copy()
    
    elif keep_strategy == 'last':
        if merge_sources and 'Source_Database' in df_with_doi.columns:
            merged_sources = merge_duplicate_sources(df_with_doi, doi_column)
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='last').copy()
            df_deduplicated['Source_Database'] = df_deduplicated[doi_column].map(merged_sources)
        else:
            df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='last').copy()
    
    else:
        # Fallback to 'first' if strategy is somehow invalid
        print(f"Warning: Unknown strategy '{keep_strategy}', defaulting to 'first'")
        df_deduplicated = df_with_doi.drop_duplicates(subset=[doi_column], keep='first').copy()
    
    # Combine deduplicated records with records that had no DOI
    df_final = pd.concat([df_deduplicated, df_without_doi], ignore_index=True)
    
    final_count = len(df_final)
    removed_count = initial_count - final_count
    
    print(f"\nDeduplication complete:")
    print(f"  Records removed: {removed_count}")
    print(f"  Final record count: {final_count}")
    
    # Save output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False)
    
    print(f"\nOutput saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Remove duplicate records from consolidated CSV based on DOI'
    )
    parser.add_argument('--input', '-i', required=True,
                        help='Input CSV file to deduplicate')
    parser.add_argument('--output', '-o', default='no_duplicates_consolidated.csv',
                        help='Output CSV file (default: no_duplicates_consolidated.csv)')
    parser.add_argument('--strategy', '-s', 
                        choices=['most_complete', 'first', 'last'], 
                        default='most_complete',
                        help='Strategy for keeping records: most_complete (default), first, or last')
    parser.add_argument('--no-merge-sources', action='store_true',
                        help='Do not merge Source_Database information from duplicates')
    parser.add_argument('--doi-column', '-d', default='DOI',
                        help='Name of the DOI column (default: DOI)')
    
    args = parser.parse_args()
    
    deduplicate_csv(
        input_file=args.input,
        output_file=args.output,
        keep_strategy=args.strategy,
        merge_sources=not args.no_merge_sources,
        doi_column=args.doi_column
    )

if __name__ == "__main__":
    main()
