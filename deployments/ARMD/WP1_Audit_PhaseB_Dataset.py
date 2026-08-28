"""
WP1 Audit – Phase B Dataset
===========================
Inspects Analysis_Ready_Positive_Cultures.parquet to understand:
- Schema (columns, types)
- Sample values
- Relationship between organisms, antibiotics, and susceptibilities
- Placeholders and missing values
- Susceptibility value formats (S/I/R vs words)
- Distribution of list lengths
- Whether pairing is valid
"""

import duckdb
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from utils.io import save_and_audit

# --------------------------------------------------------------
# Configuration
# --------------------------------------------------------------
INPUT_PARQUET = "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet"
OUTPUT_DIR = "output/WP1 – Audit – PhaseB"
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")

print("=" * 70)
print("WP1 AUDIT: ANALYSIS-READY POSITIVE CULTURE DATASET")
print("=" * 70)

# --------------------------------------------------------------
# 1. Schema inspection
# --------------------------------------------------------------
print("\n1. SCHEMA")
print("-" * 40)
schema = con.execute(f"DESCRIBE SELECT * FROM read_parquet('{INPUT_PARQUET}')").df()
print(schema.to_string(index=False))
schema.to_csv(os.path.join(OUTPUT_DIR, "01_Schema.csv"), index=False)

# --------------------------------------------------------------
# 2. Row count and basic stats
# --------------------------------------------------------------
total_rows = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}')").fetchone()[0]
print(f"\nTotal rows: {total_rows:,}")

# --------------------------------------------------------------
# 3. Sample rows (first 10, random 10)
# --------------------------------------------------------------
sample_first = con.execute(f"SELECT * FROM read_parquet('{INPUT_PARQUET}') LIMIT 10").df()
sample_random = con.execute(f"SELECT * FROM read_parquet('{INPUT_PARQUET}') TABLESAMPLE 10 ROWS").df()
sample_first.to_csv(os.path.join(OUTPUT_DIR, "02_Sample_First_10.csv"), index=False)
sample_random.to_csv(os.path.join(OUTPUT_DIR, "03_Sample_Random_10.csv"), index=False)

print("\nFirst 5 rows:")
print(sample_first.head(5).to_string(index=False))

# --------------------------------------------------------------
# 4. Check key columns: organisms, antibiotics, susceptibilities
# --------------------------------------------------------------
print("\n2. KEY COLUMN PROFILES")
print("-" * 40)

# Count non-null and non-empty
for col in ['organisms', 'antibiotics', 'susceptibilities']:
    non_null = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE {col} IS NOT NULL").fetchone()[0]
    non_empty = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE TRIM({col}) != ''").fetchone()[0]
    print(f"{col}: non-null={non_null:,}, non-empty={non_empty:,}")

# Check for literal "Null" strings
for col in ['organisms', 'antibiotics', 'susceptibilities']:
    null_str = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE LOWER(TRIM({col})) = 'null'").fetchone()[0]
    print(f"{col} literal 'Null': {null_str:,}")

# --------------------------------------------------------------
# 5. List length distribution
# --------------------------------------------------------------
print("\n3. LIST LENGTH DISTRIBUTIONS")
print("-" * 40)

len_query = """
SELECT
    order_proc_id_coded,
    array_length(string_split(organisms, '; ')) AS n_org,
    array_length(string_split(antibiotics, '; ')) AS n_abx,
    array_length(string_split(susceptibilities, '; ')) AS n_susc
FROM read_parquet('{}')
WHERE organisms IS NOT NULL AND antibiotics IS NOT NULL AND susceptibilities IS NOT NULL
""".format(INPUT_PARQUET)

lengths = con.execute(len_query).df()
lengths.to_csv(os.path.join(OUTPUT_DIR, "04_List_Lengths.csv"), index=False)

print("n_org summary:")
print(lengths['n_org'].describe())
print("\nn_abx summary:")
print(lengths['n_abx'].describe())
print("\nn_susc summary:")
print(lengths['n_susc'].describe())

# Check if lengths are equal
mismatch = (lengths['n_org'] != lengths['n_abx']) | (lengths['n_abx'] != lengths['n_susc'])
mismatch_count = mismatch.sum()
print(f"\nCultures with mismatched list lengths: {mismatch_count:,} ({mismatch_count/len(lengths)*100:.2f}%)")

if mismatch_count > 0:
    # Save examples
    mismatch_examples = lengths[mismatch].head(20)
    mismatch_examples.to_csv(os.path.join(OUTPUT_DIR, "05_Mismatched_Lengths.csv"), index=False)
    print("First 20 mismatched examples saved.")

# --------------------------------------------------------------
# 6. Susceptibility value inspection
# --------------------------------------------------------------
print("\n4. SUSCEPTIBILITY VALUES")
print("-" * 40)

# Use the long table approach only if we can safely split; we'll check a sample
# We'll create a temporary view that splits a subset to see values
susc_sample = con.execute("""
SELECT DISTINCT UNNEST(string_split(susceptibilities, '; ')) AS susc_value
FROM read_parquet('{}')
WHERE susceptibilities IS NOT NULL AND susceptibilities != ''
LIMIT 100
""".format(INPUT_PARQUET)).df()

print("Sample distinct susceptibility values (first 20):")
print(susc_sample.head(20).to_string(index=False))
susc_sample.to_csv(os.path.join(OUTPUT_DIR, "06_Susceptibility_Values.csv"), index=False)

# --------------------------------------------------------------
# 7. Organism and antibiotic sample values
# --------------------------------------------------------------
print("\n5. ORGANISM AND ANTIBIOTIC SAMPLE")
print("-" * 40)

org_sample = con.execute("""
SELECT DISTINCT UNNEST(string_split(organisms, '; ')) AS org
FROM read_parquet('{}')
WHERE organisms IS NOT NULL AND organisms != ''
LIMIT 50
""".format(INPUT_PARQUET)).df()
print("Top 20 organisms:")
print(org_sample.head(20).to_string(index=False))

abx_sample = con.execute("""
SELECT DISTINCT UNNEST(string_split(antibiotics, '; ')) AS abx
FROM read_parquet('{}')
WHERE antibiotics IS NOT NULL AND antibiotics != ''
LIMIT 50
""".format(INPUT_PARQUET)).df()
print("Top 20 antibiotics:")
print(abx_sample.head(20).to_string(index=False))

# --------------------------------------------------------------
# 8. Check if susceptibilities are simple (S/I/R) or words
# --------------------------------------------------------------
susc_simple = con.execute("""
SELECT COUNT(*) FROM read_parquet('{}')
WHERE susceptibilities IS NOT NULL
  AND susceptibilities NOT LIKE '%Resistant%'
  AND susceptibilities NOT LIKE '%Susceptible%'
  AND susceptibilities NOT LIKE '%Intermediate%'
  AND susceptibilities NOT LIKE '%S%'
  AND susceptibilities NOT LIKE '%I%'
  AND susceptibilities NOT LIKE '%R%'
""".format(INPUT_PARQUET)).fetchone()[0]

print(f"\nRows with susceptibility values not containing typical keywords: {susc_simple:,}")

# --------------------------------------------------------------
# 9. Check for duplicates
# --------------------------------------------------------------
dup_check = con.execute(f"""
SELECT COUNT(*) - COUNT(DISTINCT order_proc_id_coded) AS dup_cultures
FROM read_parquet('{INPUT_PARQUET}')
""").fetchone()[0]
print(f"\nDuplicate culture IDs: {dup_cultures:,}")

# --------------------------------------------------------------
# 10. Missing ordering mode and specimen
# --------------------------------------------------------------
missing_mode = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE ordering_mode IS NULL OR TRIM(ordering_mode) = ''").fetchone()[0]
missing_spec = con.execute(f"SELECT COUNT(*) FROM read_parquet('{INPUT_PARQUET}') WHERE culture_description IS NULL OR TRIM(culture_description) = ''").fetchone()[0]
print(f"\nMissing ordering_mode: {missing_mode:,}")
print(f"Missing culture_description: {missing_spec:,}")

# --------------------------------------------------------------
# 11. Save complete audit summary
# --------------------------------------------------------------
report_lines = []
report_lines.append("=" * 70)
report_lines.append("WP1 AUDIT REPORT: PHASE B DATASET")
report_lines.append("=" * 70)
report_lines.append(f"Report generated: {datetime.now().isoformat()}")
report_lines.append(f"Input file: {INPUT_PARQUET}")
report_lines.append("")
report_lines.append(f"Total rows: {total_rows:,}")
report_lines.append(f"Total cultures: {con.execute(f'SELECT COUNT(DISTINCT order_proc_id_coded) FROM read_parquet(''{INPUT_PARQUET}'')').fetchone()[0]:,}")
report_lines.append("")
report_lines.append("Schema:")
for _, row in schema.iterrows():
    report_lines.append(f"  {row['column_name']}: {row['column_type']}")
report_lines.append("")
report_lines.append("List length summary:")
report_lines.append(f"  n_org: mean={lengths['n_org'].mean():.2f}, max={lengths['n_org'].max()}, min={lengths['n_org'].min()}")
report_lines.append(f"  n_abx: mean={lengths['n_abx'].mean():.2f}, max={lengths['n_abx'].max()}, min={lengths['n_abx'].min()}")
report_lines.append(f"  n_susc: mean={lengths['n_susc'].mean():.2f}, max={lengths['n_susc'].max()}, min={lengths['n_susc'].min()}")
report_lines.append(f"  Mismatched cultures: {mismatch_count:,} ({mismatch_count/len(lengths)*100:.2f}%)")
report_lines.append("")
report_lines.append("Susceptibility sample:")
for val in susc_sample['susc_value'].head(10).tolist():
    report_lines.append(f"  '{val}'")
report_lines.append("")
report_lines.append("Duplicate culture IDs: {dup_cultures:,}")
report_lines.append("Missing ordering_mode: {missing_mode:,}")
report_lines.append("Missing culture_description: {missing_spec:,}")
report_lines.append("")
report_lines.append("=" * 70)

report_file = os.path.join(OUTPUT_DIR, "Audit_Report.txt")
with open(report_file, 'w') as f:
    f.write("\n".join(report_lines))

print("\n✅ Audit report written to:", report_file)

# --------------------------------------------------------------
# 12. Completion
# --------------------------------------------------------------
print("\n" + "=" * 70)
print("AUDIT COMPLETED")
print("=" * 70)
print(f"All outputs saved to: {OUTPUT_DIR}")

con.close()