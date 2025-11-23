# RIS Search Export Consolidation Tools

Tools to consolidate bibliographic data from ScienceDirect, Scopus, and Web of Science **search results** into a single unified CSV file.

## Table of Contents

1. [**ris_to_csv.py**](#tool-1-ris-to-csv-converter) - Convert RIS bibliography files to CSV/Excel format
2. [**consolidate_databases.py**](#tool-2-database-export-consolidator) - Merge multiple database exports into a single unified file
3. [**deduplicate.py**](#tool-3-duplicate-remover) - Remove duplicate records from consolidated CSV files based on DOI
4. [**Complete Workflow Example**](#complete-workflow-example) - End-to-end process

## Requirements

```bash
pip install pandas rispy openpyxl
```

---

## Tool 1: RIS to CSV Converter

Converts one or more RIS (Research Information Systems) files into CSV or Excel format.

### Features

- Processes multiple RIS files from a folder
- Combines all entries into a single output file
- Supports CSV and Excel output formats
- Configurable input/output paths

### Usage

#### Basic Usage

Convert all RIS files in the `ris` folder to CSV:

```bash
python ris_to_csv.py
```

This processes all `.ris` files in the `ris` folder and creates `output/exported.csv`.

#### Custom Input Folder

```bash
python ris_to_csv.py --input my_ris_folder
```

#### Custom Output Location and Filename

```bash
python ris_to_csv.py --output results --filename bibliography
```

#### Export to Excel

```bash
python ris_to_csv.py --format xlsx
```

#### Export to Both CSV and Excel

```bash
python ris_to_csv.py --format both
```

#### Full Custom Example

```bash
python ris_to_csv.py \
  -i papers/ris \
  -o papers/exports \
  -f bibliography \
  -t both
```

### Command-Line Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--input` | `-i` | `ris` | Input folder containing .ris files |
| `--output` | `-o` | `output` | Output folder |
| `--filename` | `-f` | `exported` | Output filename without extension |
| `--format` | `-t` | `csv` | Output format: `csv`, `xlsx`, or `both` |

### Example Output

```
Found 3 .ris file(s)
Processing references_1.ris...
Processing references_2.ris...
Processing references_3.ris...
Total entries: 150
Exported to output/exported.csv
```

---

## Tool 2: Database Export Consolidator

Consolidates bibliographic data from ScienceDirect, Scopus, and Web of Science into a single unified CSV file.

### Features

- Merges three different database exports into one consolidated file
- Uses external JSON configuration for column mappings
- Preserves all information without data loss
- Intelligent column ordering (common fields first, then two-source fields, then single-source fields)
- Optional source tracking column
- Automatic DOI link generation for records missing links
- Flexible command-line interface

### Usage

#### Basic Usage

Consolidate three database exports with default settings:

```bash
python consolidate_databases.py \
  --sciencedirect sciencedirect.csv \
  --scopus scopus.csv \
  --webofscience webofscience.csv
```

This creates `consolidated_output.csv` in the current directory.

#### Custom Output and Configuration

Specify custom paths for input files, output file, and mapping configuration:

```bash
python consolidate_databases.py \
  -sd data/sciencedirect.csv \
  -sc data/scopus.csv \
  -wos data/webofscience.csv \
  -c my_mapping.json \
  -o results/consolidated.csv
```

#### Without Source Column

By default, the tool adds a `Source_Database` column to track each record's origin. To omit this:

```bash
python consolidate_databases.py \
  --sciencedirect sd.csv \
  --scopus sc.csv \
  --webofscience wos.csv \
  --no-source-column
```

### Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--sciencedirect` | `-sd` | Yes | - | Path to ScienceDirect CSV file |
| `--scopus` | `-sc` | Yes | - | Path to Scopus CSV file |
| `--webofscience` | `-wos` | Yes | - | Path to Web of Science CSV file |
| `--config` | `-c` | No | `column_mapping.json` | Path to column mapping JSON file |
| `--output` | `-o` | No | `consolidated_output.csv` | Output CSV file path |
| `--no-source-column` | - | No | - | Do not add Source_Database column |

### Column Mapping Configuration

The `column_mapping.json` file defines how columns from each database are mapped to unified column names. The structure is:

```json
{
  "unified_schema": [
    {
      "unified_name": "Title",
      "mappings": {
        "sciencedirect": "primary_title",
        "scopus": "Title",
        "webofscience": "Article Title"
      },
      "priority": 1
    }
  ]
}
```

#### Priority Levels

- **Priority 1**: Columns present in all three databases
- **Priority 2**: Columns present in two databases
- **Priority 3**: Columns present in only one database

Output columns are ordered by priority first, then alphabetically within each priority level.

### Customizing Mappings

To customize column mappings:

1. Edit `column_mapping.json`
2. Modify `unified_name` to change output column names
3. Update `mappings` to match your source column names
4. Adjust `priority` to control column ordering

No code changes needed - just update the JSON file and run the script.

### Output

The consolidated CSV includes:
- `Source_Database` column (optional) - identifies the origin of each record
- All mapped columns from the unified schema
- `DOI_Link` column automatically generated for records with DOI (uses `https://doi.org/{DOI}` format)
- Missing values as empty cells where data isn't available from a source

### Example Output

```
Source_Database,Title,Authors,Year,DOI,DOI_Link,Abstract,...
ScienceDirect,Enhancing emotional response...,['Bayro, Allison'...],2025,10.1016/j.cag.2025.104196,https://doi.org/10.1016/j.cag.2025.104196,Accurate and efficient...
Scopus,From local to global...,"Li, X.; Huang, J...",2026,10.1016/j.bspc.2025.109068,https://doi.org/10.1016/j.bspc.2025.109068,
Web of Science,EmotiW 2018: Audio-Video...,"Dhall, A; Kaur, A...",2018,10.1145/3242969.3264978,https://doi.org/10.1145/3242969.3264978,
```

---

## Tool 3: Duplicate Remover

Removes duplicate records from consolidated CSV files by comparing DOIs and keeping the most complete record.

### Features

- Identifies duplicates based on DOI (most reliable bibliographic identifier)
- Multiple strategies for handling duplicates (most complete, first, last)
- Merges source information to show which databases contained the duplicate
- Preserves records without DOI
- Detailed reporting of duplicates found and removed

### Usage

#### Basic Usage

Remove duplicates keeping the most complete record:

```bash
python deduplicate.py --input consolidated_output.csv
```

This creates `no_duplicates_consolidated.csv` with duplicates removed.

#### Custom Output Filename

```bash
python deduplicate.py -i consolidated_output.csv -o cleaned_bibliography.csv
```

#### Different Strategies

Keep first occurrence instead of most complete:

```bash
python deduplicate.py -i consolidated_output.csv -s first
```

Keep last occurrence:

```bash
python deduplicate.py -i consolidated_output.csv -s last
```

#### Without Source Merging

By default, when duplicates are found, the tool merges source information (e.g., "ScienceDirect, Scopus"). To disable this:

```bash
python deduplicate.py -i consolidated_output.csv --no-merge-sources
```

#### Custom DOI Column Name

If your CSV uses a different column name for DOI:

```bash
python deduplicate.py -i myfile.csv --doi-column MY_DOI_COLUMN
```

### Command-Line Arguments

| Argument | Short | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `--input` | `-i` | Yes | - | Input CSV file to deduplicate |
| `--output` | `-o` | No | `no_duplicates_consolidated.csv` | Output CSV file |
| `--strategy` | `-s` | No | `most_complete` | Strategy: `most_complete`, `first`, or `last` |
| `--no-merge-sources` | - | No | - | Do not merge Source_Database information |
| `--doi-column` | `-d` | No | `DOI` | Name of the DOI column |

### Deduplication Strategies

- **most_complete** (default) - Keeps the record with the most non-null fields, ensuring maximum information retention
- **first** - Keeps the first occurrence of each DOI
- **last** - Keeps the last occurrence of each DOI

### Example Output

```
Loading consolidated_output.csv...
Initial record count: 1778
Warning: 32 records have no DOI and cannot be checked for duplicates.

Duplicate analysis:
  Records with duplicates: 437
  Unique DOIs with duplicates: 218

Example duplicates found:
  DOI: 10.1016/j.bspc.2025.109068
    Found in: Scopus, Web of Science
    Title: From local to global: A hierarchical spatial-frequency Bi-pa...

Applying deduplication strategy: most_complete
Merging source information from duplicates...

Deduplication complete:
  Records removed: 219
  Final record count: 1559

Output saved to: no_duplicates_consolidated.csv
```

### Understanding the Output

- Records with the same DOI are considered duplicates
- The strategy determines which record to keep
- When source merging is enabled, the `Source_Database` column shows all databases that contained the record (e.g., "Scopus, Web of Science")
- Records without a DOI are preserved but cannot be checked for duplicates

---

## Complete Workflow Example

A typical end-to-end workflow to consolidate and deduplicate search results from multiple databases:

```bash
# Step 1: Convert RIS files to CSV (if needed)
python ris_to_csv.py -i exports/ris -o exports/csv -f sciencedirect

# Step 2: Consolidate all database exports
python consolidate_databases.py \
  -sd exports/csv/sciencedirect.csv \
  -sc exports/scopus.csv \
  -wos exports/webofscience.csv \
  -o output/consolidated.csv

# Step 3: Remove duplicates
python deduplicate.py \
  -i output/consolidated.csv \
  -o output/final_bibliography.csv
```

### Alternative: Compact Workflow

```bash
# Quick consolidation and deduplication with defaults
python ris_to_csv.py -i ris_files
python consolidate_databases.py -sd sd.csv -sc scopus.csv -wos wos.csv
python deduplicate.py -i consolidated_output.csv
```

---

## Files Included

- `ris_to_csv.py` - RIS to CSV/Excel conversion script
- `consolidate_databases.py` - Database consolidation script
- `deduplicate.py` - Duplicate removal script
- `column_mapping.json` - Column mapping configuration file
- `README.md` - This documentation

## License

MIT
