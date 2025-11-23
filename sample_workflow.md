# Sample Workflow

---

## Step 1 - Convert RIS to CSV
```bash
python ris_to_csv.py -i papers/ris -o output
```

## Step 2 - Consolidate files exported into a single file
```bash
python consolidate_databases.py -sd output/sciencedirect.csv -sc output/scopus.csv -wos output/webofscience.csv --output output/consolidated.csv
```

## Step 3 - Eliminate duplicates from the consolidated file 
```bash
python deduplicate.py -i output/consolidated.csv -o output/no_duplicates.csv
```
