"""
Work Package 1 - Phase A - Step 3
Validate Field Consistency Within Each Culture Order
"""

import duckdb
import pandas as pd
import os

# ----------------------------------------------------------
# Output folder
# ----------------------------------------------------------
OUTPUT_DIR = os.path.join("output", "WP1 – Phase A – Step 3")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------------------------
# Connect to DuckDB
# ----------------------------------------------------------
con = duckdb.connect("armd.db")

# ----------------------------------------------------------
# Load microbiology cohort
# ----------------------------------------------------------
con.execute("""
CREATE OR REPLACE VIEW cohort AS
SELECT *
FROM read_csv_auto('Data/microbiology_cultures_cohort.csv')
""")

# ----------------------------------------------------------
# Fields expected to remain constant within a culture order
# ----------------------------------------------------------
constant_fields = [
    "anon_id",
    "pat_enc_csn_id_coded",
    "order_time_jittered_utc",
    "ordering_mode",
    "culture_description",
    "was_positive"
]

id_col = "order_proc_id_coded"

summary_results = []

print("=" * 70)
print("VALIDATING FIELD CONSISTENCY WITHIN CULTURE ORDERS")
print("=" * 70)

# ----------------------------------------------------------
# Check each field independently
# ----------------------------------------------------------
for field in constant_fields:

    print(f"\nChecking: {field}")

    query = f"""
    SELECT
        {id_col},
        COUNT(DISTINCT {field}) AS n_values
    FROM cohort
    GROUP BY {id_col}
    HAVING COUNT(DISTINCT {field}) > 1
    """

    inconsistent = con.execute(query).df()

    n_inconsistent = len(inconsistent)

    print(f"Inconsistent culture orders: {n_inconsistent}")

    summary_results.append({
        "Field": field,
        "Inconsistent_Culture_Orders": n_inconsistent
    })

    if n_inconsistent > 0:
        inconsistent.to_csv(
            os.path.join(OUTPUT_DIR, f"WP1_Inconsistent_{field}.csv"),
            index=False
        )
        print(f"Saved: WP1_Inconsistent_{field}.csv")

# ----------------------------------------------------------
# Overall summary
# ----------------------------------------------------------
summary = pd.DataFrame(summary_results)

print("\n")
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(summary)

summary.to_csv(
    os.path.join(OUTPUT_DIR, "WP1_Table9_Field_Consistency_Summary.csv"),
    index=False
)

# ----------------------------------------------------------
# Final conclusion
# ----------------------------------------------------------
if summary["Inconsistent_Culture_Orders"].sum() == 0:
    print("\n✅ All evaluated fields are consistent within culture orders.")
    print("Aggregation to one row per culture order can proceed.")
else:
    print("\n⚠️ Some fields are inconsistent.")
    print("Review the exported inconsistency files before aggregation.")

print("\nOutputs generated:")
print(f"  - {OUTPUT_DIR}/WP1_Table9_Field_Consistency_Summary.csv")

for field in constant_fields:
    if (summary.loc[
        summary["Field"] == field,
        "Inconsistent_Culture_Orders"
    ].iloc[0] > 0):
        print(f"  - {OUTPUT_DIR}/WP1_Inconsistent_{field}.csv")

con.close()