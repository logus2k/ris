# Search Export Consolidation Tools

Tools to consolidate bibliographic data from ScienceDirect, Scopus, and Web of Science **search results** into a single unified CSV file.

## Tools Overview

This package includes two tools:

1. **ris_to_csv.py** - Convert RIS bibliography files to CSV/Excel format
2. **consolidate_databases.py** - Merge multiple database exports into a single unified file

## Requirements

```bash
pip install pandas rispy openpyxl
```

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
- Missing values as empty cells where data isn't available from a source

### Example Output

```
Source_Database,Title,Authors,Year,DOI,Abstract,...
ScienceDirect,Enhancing emotional response...,['Bayro, Allison'...],2025,10.1016/j.cag.2025.104196,Accurate and efficient...
Scopus,From local to global...,"Li, X.; Huang, J...",2026,10.1016/j.bspc.2025.109068,
Web of Science,EmotiW 2018: Audio-Video...,"Dhall, A; Kaur, A...",2018,,
```

---

## Complete Workflow Example

A typical workflow to consolidate search results from multiple databases:

```bash
# Step 1: Convert RIS files to CSV (if needed)
python ris_to_csv.py -i exports/ris -o exports/csv -f sciencedirect

# Step 2: Consolidate all database exports
python consolidate_databases.py \
  -sd exports/csv/sciencedirect.csv \
  -sc exports/scopus.csv \
  -wos exports/webofscience.csv \
  -o final/consolidated_bibliography.csv
```

## Files Included

- `ris_to_csv.py` - RIS to CSV/Excel conversion script
- `consolidate_databases.py` - Database consolidation script
- `column_mapping.json` - Column mapping configuration file
- `README.md` - This documentation

## License

MIT.
