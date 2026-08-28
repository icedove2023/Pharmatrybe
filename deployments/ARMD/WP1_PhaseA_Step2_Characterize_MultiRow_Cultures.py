"""
Work Package 1 - Phase A - Step 2
Characterize the Structure of Multi-row Culture Orders
"""

import duckdb
import pandas as pd
import os

# ----------------------------------------------------------
# Paths and output folder
# ----------------------------------------------------------
CSV_PATH = "Data/microbiology_cultures_cohort.csv"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase A – Step 2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------
# Connect to DuckDB
# ----------------------------------------------------------
con = duckdb.connect("armd.db")

# Load cohort view
con.execute(f"""
CREATE OR REPLACE VIEW cohort AS
SELECT *
FROM read_csv_auto('{CSV_PATH}')
""")

# ----------------------------------------------------------
# Summarize each culture order
# ----------------------------------------------------------
culture_structure = con.execute("""

SELECT

    order_proc_id_coded,

    COUNT(*) AS total_rows,

    COUNT(DISTINCT organism) AS n_organisms,

    COUNT(DISTINCT antibiotic) AS n_antibiotics,

    COUNT(DISTINCT susceptibility) AS n_susceptibility,

    MAX(was_positive) AS was_positive,

    MIN(culture_description) AS culture_description,

    MIN(ordering_mode) AS ordering_mode

FROM cohort

GROUP BY order_proc_id_coded

ORDER BY total_rows DESC

""").df()

# ----------------------------------------------------------
# Save complete structure table
# ----------------------------------------------------------
culture_structure.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table4_Culture_Structure.csv"),
    index=False
)

# ----------------------------------------------------------
# Overall summaries
# ----------------------------------------------------------
print("=" * 60)
print("CULTURE STRUCTURE SUMMARY")
print("=" * 60)

print("\nRows per culture")
print(culture_structure["total_rows"].describe())

print("\nDistinct organisms")
print(culture_structure["n_organisms"].describe())

print("\nDistinct antibiotics")
print(culture_structure["n_antibiotics"].describe())

print("\nDistinct susceptibility values")
print(culture_structure["n_susceptibility"].describe())

# ----------------------------------------------------------
# Distribution of organism counts
# ----------------------------------------------------------
organism_distribution = (
    culture_structure["n_organisms"]
    .value_counts()
    .sort_index()
    .reset_index()
)

organism_distribution.columns = [
    "Number_of_Organisms",
    "Culture_Orders"
]

print("\n")
print("=" * 60)
print("ORGANISM DISTRIBUTION")
print("=" * 60)
print(organism_distribution)

organism_distribution.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table5_Organism_Distribution.csv"),
    index=False
)

# ----------------------------------------------------------
# Distribution of antibiotic counts
# ----------------------------------------------------------
antibiotic_distribution = (
    culture_structure["n_antibiotics"]
    .value_counts()
    .sort_index()
    .reset_index()
)

antibiotic_distribution.columns = [
    "Number_of_Antibiotics",
    "Culture_Orders"
]

print("\n")
print("=" * 60)
print("ANTIBIOTIC DISTRIBUTION")
print("=" * 60)
print(antibiotic_distribution)

antibiotic_distribution.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table6_Antibiotic_Distribution.csv"),
    index=False
)

# ----------------------------------------------------------
# Positive vs Negative cultures
# ----------------------------------------------------------
positivity = (
    culture_structure["was_positive"]
    .value_counts(dropna=False)
    .reset_index()
)

positivity.columns = [
    "was_positive",
    "Culture_Orders"
]

print("\n")
print("=" * 60)
print("CULTURE POSITIVITY")
print("=" * 60)
print(positivity)

positivity.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table7_Culture_Positivity.csv"),
    index=False
)

# ----------------------------------------------------------
# Cultures with largest structures
# ----------------------------------------------------------
top20 = culture_structure.nlargest(20, "total_rows")

top20.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table8_Largest_Cultures.csv"),
    index=False
)

print("\n")
print("=" * 60)
print("TOP 20 MOST COMPLEX CULTURE ORDERS")
print("=" * 60)
print(top20[["order_proc_id_coded", "total_rows", "n_organisms", "n_antibiotics"]])

# ----------------------------------------------------------
# Completion
# ----------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 2 COMPLETED SUCCESSFULLY")
print("=" * 60)
print(f"All outputs saved to: '{OUTPUT_DIR}/'")
print("  - WP1_Table4_Culture_Structure.csv")
print("  - WP1_Table5_Organism_Distribution.csv")
print("  - WP1_Table6_Antibiotic_Distribution.csv")
print("  - WP1_Table7_Culture_Positivity.csv")
print("  - WP1_Table8_Largest_Cultures.csv")

con.close()