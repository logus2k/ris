import pandas as pd
import json
import argparse
from pathlib import Path

def load_config(config_path):
    """Load the column mapping configuration from JSON file."""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def consolidate_databases(sciencedirect_file, scopus_file, webofscience_file, 
                          config_file, output_file, add_source_column=True):
    """
    Consolidate three database export files into a single CSV.
    
    Args:
        sciencedirect_file: Path to ScienceDirect CSV
        scopus_file: Path to Scopus CSV
        webofscience_file: Path to Web of Science CSV
        config_file: Path to column mapping JSON
        output_file: Path for output CSV
        add_source_column: Whether to add a 'Source_Database' column
    """
    
    # Load configuration
    config = load_config(config_file)
    schema = config['unified_schema']
    
    # Sort schema by priority (1=all three, 2=two sources, 3=one source)
    schema_sorted = sorted(schema, key=lambda x: (x['priority'], x['unified_name']))
    
    # Load the three databases
    print("Loading database files...")
    sd_df = pd.read_csv(sciencedirect_file)
    scopus_df = pd.read_csv(scopus_file)
    wos_df = pd.read_csv(webofscience_file)
    
    print(f"  ScienceDirect: {len(sd_df)} records")
    print(f"  Scopus: {len(scopus_df)} records")
    print(f"  Web of Science: {len(wos_df)} records")
    
    # Create unified dataframes for each source
    print("\nMapping columns to unified schema...")
    
    def map_to_unified(df, source_name, schema):
        """Map a dataframe to the unified schema."""
        unified_df = pd.DataFrame()
        
        for field in schema:
            unified_col = field['unified_name']
            mappings = field['mappings']
            
            if source_name in mappings:
                source_col = mappings[source_name]
                if source_col in df.columns:
                    unified_df[unified_col] = df[source_col]
                else:
                    unified_df[unified_col] = None
            else:
                unified_df[unified_col] = None
        
        return unified_df
    
    sd_unified = map_to_unified(sd_df, 'sciencedirect', schema_sorted)
    scopus_unified = map_to_unified(scopus_df, 'scopus', schema_sorted)
    wos_unified = map_to_unified(wos_df, 'webofscience', schema_sorted)
    
    # Add source column if requested
    if add_source_column:
        sd_unified.insert(0, 'Source_Database', 'ScienceDirect')
        scopus_unified.insert(0, 'Source_Database', 'Scopus')
        wos_unified.insert(0, 'Source_Database', 'Web of Science')
    
    # Concatenate all dataframes
    print("\nCombining all records...")
    consolidated_df = pd.concat([sd_unified, scopus_unified, wos_unified], 
                                 ignore_index=True)
    
    # Save to CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    consolidated_df.to_csv(output_path, index=False)
    
    print(f"\nConsolidated {len(consolidated_df)} records")
    print(f"Output file: {output_path}")
    print(f"Total columns: {len(consolidated_df.columns)}")
    
    # Print column summary
    print("\nColumn priority summary:")
    priority_counts = {}
    for field in schema_sorted:
        priority = field['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1
    
    print(f"  Priority 1 (in all 3 sources): {priority_counts.get(1, 0)} columns")
    print(f"  Priority 2 (in 2 sources): {priority_counts.get(2, 0)} columns")
    print(f"  Priority 3 (in 1 source): {priority_counts.get(3, 0)} columns")

def main():
    parser = argparse.ArgumentParser(
        description='Consolidate ScienceDirect, Scopus, and Web of Science exports into a single CSV'
    )
    parser.add_argument('--sciencedirect', '-sd', required=True, 
                        help='Path to ScienceDirect CSV file')
    parser.add_argument('--scopus', '-sc', required=True, 
                        help='Path to Scopus CSV file')
    parser.add_argument('--webofscience', '-wos', required=True, 
                        help='Path to Web of Science CSV file')
    parser.add_argument('--config', '-c', default='column_mapping.json', 
                        help='Path to column mapping JSON file (default: column_mapping.json)')
    parser.add_argument('--output', '-o', default='consolidated_output.csv', 
                        help='Output CSV file path (default: consolidated_output.csv)')
    parser.add_argument('--no-source-column', action='store_true', 
                        help='Do not add Source_Database column')
    
    args = parser.parse_args()
    
    consolidate_databases(
        sciencedirect_file=args.sciencedirect,
        scopus_file=args.scopus,
        webofscience_file=args.webofscience,
        config_file=args.config,
        output_file=args.output,
        add_source_column=not args.no_source_column
    )

if __name__ == "__main__":
    main()
