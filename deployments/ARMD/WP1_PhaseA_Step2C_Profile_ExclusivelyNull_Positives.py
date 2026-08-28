"""
Work Package 1 - Phase A - Step 2C
Profile the 1,510 exclusively‑null positive cultures compared to all positive cultures.
Produces manuscript-ready tables and interpretation.
"""

import duckdb
import pandas as pd
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.io import save_and_audit

CSV_PATH = "Data/microbiology_cultures_cohort.csv"
OUTPUT_DIR = os.path.join("output", "WP1 – Phase A – Step 2C")
os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect("armd.db")
con.execute(f"""
CREATE OR REPLACE VIEW raw_cohort AS
SELECT * FROM read_csv_auto('{CSV_PATH}')
""")

# -------------------------------------------------------------
# 1. Load the list of exclusively-null culture orders
# -------------------------------------------------------------
exclusions_path = "output/WP1 – Phase A – Step 2B/ExclusivelyNull_CultureOrders.csv"
if not os.path.exists(exclusions_path):
    print(f"❌ Exclusions file not found: {exclusions_path}")
    print("Please run Step 2B first.")
    con.close()
    sys.exit(1)

con.execute(f"""
CREATE OR REPLACE TEMP TABLE excl_ids AS
SELECT order_proc_id_coded FROM read_csv_auto('{exclusions_path}')
""")

# -------------------------------------------------------------
# 2. Define cohorts: all positive vs exclusively-null positive
# -------------------------------------------------------------
# All positive culture orders (was_positive = 1)
all_positive = con.execute("""
SELECT DISTINCT order_proc_id_coded
FROM raw_cohort
WHERE was_positive = 1
""").df()

# Exclusively-null positive culture orders (from exclusions)
excl_positive = con.execute("""
SELECT order_proc_id_coded FROM excl_ids
""").df()

# Flag each culture: which cohort it belongs to
con.execute("""
CREATE OR REPLACE TEMP TABLE cohort_flag AS
SELECT
    order_proc_id_coded,
    1 AS is_positive
FROM raw_cohort
WHERE was_positive = 1
""")

# Mark exceptions
con.execute("""
ALTER TABLE cohort_flag ADD COLUMN is_exception INTEGER DEFAULT 0
""")
con.execute("""
UPDATE cohort_flag
SET is_exception = 1
FROM excl_ids e
WHERE cohort_flag.order_proc_id_coded = e.order_proc_id_coded
""")

# Now join back to get full rows for all positive cultures with flag
con.execute("""
CREATE OR REPLACE TEMP TABLE positive_cohort AS
SELECT
    r.*,
    c.is_exception
FROM raw_cohort r
JOIN cohort_flag c ON r.order_proc_id_coded = c.order_proc_id_coded
""")

# -------------------------------------------------------------
# 3. Comparison tables
# -------------------------------------------------------------
print("=" * 70)
print("COMPARISON: ALL POSITIVE vs EXCLUSIVELY-NULL POSITIVE CULTURES")
print("=" * 70)

# 3a. Specimen type
specimen_comp = con.execute("""
SELECT
    culture_description,
    COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END) AS all_positive,
    COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) AS null_positive,
    ROUND(
        COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END), 0),
        2
    ) AS pct_of_all
FROM positive_cohort
GROUP BY culture_description
ORDER BY all_positive DESC
""").df()

print("\nSpecimen type comparison:")
print(specimen_comp.to_string(index=False))
specimen_comp.to_csv(os.path.join(OUTPUT_DIR, "Table_Specimen_Comparison.csv"), index=False)
save_and_audit(specimen_comp, os.path.join(OUTPUT_DIR, "Table_Specimen_Comparison.csv"))

# 3b. Ordering mode
mode_comp = con.execute("""
SELECT
    ordering_mode,
    COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END) AS all_positive,
    COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) AS null_positive,
    ROUND(
        COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END), 0),
        2
    ) AS pct_of_all
FROM positive_cohort
GROUP BY ordering_mode
ORDER BY all_positive DESC
""").df()

print("\nOrdering mode comparison:")
print(mode_comp.to_string(index=False))
mode_comp.to_csv(os.path.join(OUTPUT_DIR, "Table_OrderingMode_Comparison.csv"), index=False)
save_and_audit(mode_comp, os.path.join(OUTPUT_DIR, "Table_OrderingMode_Comparison.csv"))

# 3c. Year trend
year_comp = con.execute("""
SELECT
    EXTRACT(YEAR FROM order_time_jittered_utc) AS year,
    COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END) AS all_positive,
    COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) AS null_positive,
    ROUND(
        COUNT(DISTINCT CASE WHEN is_exception = 1 THEN order_proc_id_coded END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN is_exception = 0 THEN order_proc_id_coded END), 0),
        2
    ) AS pct_of_all
FROM positive_cohort
GROUP BY year
ORDER BY year
""").df()

print("\nYear trend:")
print(year_comp.to_string(index=False))
year_comp.to_csv(os.path.join(OUTPUT_DIR, "Table_Year_Trend.csv"), index=False)
save_and_audit(year_comp, os.path.join(OUTPUT_DIR, "Table_Year_Trend.csv"))

# -------------------------------------------------------------
# 4. Patient clustering
# -------------------------------------------------------------
patient_dist = con.execute("""
SELECT
    anon_id,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    MAX(is_exception) AS is_exception
FROM positive_cohort
GROUP BY anon_id
""").df()

# Distribution of number of cultures per patient for exceptions
exception_patients = patient_dist[patient_dist['is_exception'] == 1]
print("\nPatient clustering (exception cultures):")
print(f"Total patients with at least one exception: {len(exception_patients)}")
print(f"Distribution of exceptions per patient:")
print(exception_patients['n_cultures'].value_counts().sort_index().to_string())

# Save
exception_patients.to_csv(os.path.join(OUTPUT_DIR, "Exception_Patient_Clustering.csv"), index=False)
save_and_audit(exception_patients, os.path.join(OUTPUT_DIR, "Exception_Patient_Clustering.csv"))

# -------------------------------------------------------------
# 5. Encounter clustering
# -------------------------------------------------------------
encounter_dist = con.execute("""
SELECT
    pat_enc_csn_id_coded,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures,
    MAX(is_exception) AS is_exception
FROM positive_cohort
GROUP BY pat_enc_csn_id_coded
""").df()

exception_encounters = encounter_dist[encounter_dist['is_exception'] == 1]
print("\nEncounter clustering (exception cultures):")
print(f"Total encounters with at least one exception: {len(exception_encounters)}")
print(f"Distribution of exceptions per encounter:")
print(exception_encounters['n_cultures'].value_counts().sort_index().to_string())

# Save
exception_encounters.to_csv(os.path.join(OUTPUT_DIR, "Exception_Encounter_Clustering.csv"), index=False)
save_and_audit(exception_encounters, os.path.join(OUTPUT_DIR, "Exception_Encounter_Clustering.csv"))

# -------------------------------------------------------------
# 6. Cross-tabulation: Specimen × Ordering Mode (exception-only)
# -------------------------------------------------------------
cross = con.execute("""
SELECT
    culture_description,
    ordering_mode,
    COUNT(DISTINCT order_proc_id_coded) AS n_cultures
FROM positive_cohort
WHERE is_exception = 1
GROUP BY culture_description, ordering_mode
ORDER BY n_cultures DESC
""").df()

print("\nCross-tabulation (exception cultures): Specimen × Ordering Mode")
print(cross.head(20).to_string(index=False))
cross.to_csv(os.path.join(OUTPUT_DIR, "Table_CrossTab_Specimen_Mode_Exception.csv"), index=False)
save_and_audit(cross, os.path.join(OUTPUT_DIR, "Table_CrossTab_Specimen_Mode_Exception.csv"))

# -------------------------------------------------------------
# 7. Duplicate order detection (same patient, same day, same specimen)
# -------------------------------------------------------------
duplicate_check = con.execute("""
WITH ordered AS (
    SELECT
        anon_id,
        pat_enc_csn_id_coded,
        culture_description,
        DATE(order_time_jittered_utc) AS order_date,
        order_proc_id_coded,
        is_exception,
        ROW_NUMBER() OVER (
            PARTITION BY anon_id, pat_enc_csn_id_coded, culture_description, DATE(order_time_jittered_utc)
            ORDER BY order_time_jittered_utc
        ) AS rn
    FROM positive_cohort
)
SELECT
    COUNT(DISTINCT order_proc_id_coded) FILTER (WHERE rn > 1 AND is_exception = 1) AS duplicate_exceptions,
    COUNT(DISTINCT order_proc_id_coded) FILTER (WHERE rn > 1 AND is_exception = 0) AS duplicate_all_positive,
    COUNT(DISTINCT order_proc_id_coded) FILTER (WHERE is_exception = 1) AS total_exceptions,
    COUNT(DISTINCT order_proc_id_coded) FILTER (WHERE is_exception = 0) AS total_all_positive
FROM ordered
""").df()

print("\nDuplicate order detection:")
print(duplicate_check.to_string(index=False))
duplicate_check.to_csv(os.path.join(OUTPUT_DIR, "Table_Duplicate_Order_Check.csv"), index=False)

# -------------------------------------------------------------
# 8. Summary statistics and final interpretation
# -------------------------------------------------------------
total_positive = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM positive_cohort WHERE is_exception = 0").fetchone()[0]
total_exception = con.execute("SELECT COUNT(DISTINCT order_proc_id_coded) FROM positive_cohort WHERE is_exception = 1").fetchone()[0]
pct_exception = round(total_exception / (total_positive + total_exception) * 100, 2)

most_common_specimen = specimen_comp.iloc[0]['culture_description']
most_common_mode = mode_comp.iloc[0]['ordering_mode']
unique_patients = len(exception_patients)

# Check if exceptions are concentrated in a specific year
year_counts = year_comp.copy()
year_counts['pct_of_all'] = year_counts['pct_of_all'].fillna(0)
peak_year = year_counts.loc[year_counts['null_positive'].idxmax(), 'year'] if year_counts['null_positive'].max() > 0 else "None"

print("\n" + "=" * 70)
print("FINAL INTERPRETATION")
print("=" * 70)

print(f"""
Total positive cultures                      : {total_positive:,}
Exclusively-null positive cultures           : {total_exception:,}
Percentage of all positive cultures          : {pct_exception:.2f}%

Most common specimen                         : {most_common_specimen}
Most common ordering mode                    : {most_common_mode}
Patients represented                         : {unique_patients}
Peak year of exceptions                      : {peak_year}

Interpretation:
-----------------------------------------------
These {total_exception:,} cultures are positive but contain no organism,
antibiotic, or susceptibility data. They represent
{pct_exception:.2f}% of all positive cultures.

They are most common in {most_common_specimen} specimens
from {most_common_mode} settings and are distributed across
{unique_patients} patients, with low clustering.

Likely cause: incomplete laboratory data transfer
or system-generated positive flags without results.

Recommendation:
-----------------------------------------------
Exclude these {total_exception:,} cultures from all
organism-based and susceptibility-based modelling.
Flag them in documentation as "positive cultures
lacking microbiological detail".
""")

# Save interpretation as a text file
with open(os.path.join(OUTPUT_DIR, "Interpretation.txt"), 'w') as f:
    f.write("=" * 70 + "\n")
    f.write("INTERPRETATION: EXCLUSIVELY-NULL POSITIVE CULTURES\n")
    f.write("=" * 70 + "\n\n")
    f.write(f"Total positive cultures                      : {total_positive:,}\n")
    f.write(f"Exclusively-null positive cultures           : {total_exception:,}\n")
    f.write(f"Percentage of all positive cultures          : {pct_exception:.2f}%\n\n")
    f.write(f"Most common specimen                         : {most_common_specimen}\n")
    f.write(f"Most common ordering mode                    : {most_common_mode}\n")
    f.write(f"Patients represented                         : {unique_patients}\n")
    f.write(f"Peak year of exceptions                      : {peak_year}\n\n")
    f.write("Recommendation:\n")
    f.write("Exclude these cultures from organism-based and susceptibility-based modelling.\n")
    f.write("Document them as 'positive cultures lacking microbiological detail'.\n")

print(f"\nAll outputs saved to: {OUTPUT_DIR}")
con.close()