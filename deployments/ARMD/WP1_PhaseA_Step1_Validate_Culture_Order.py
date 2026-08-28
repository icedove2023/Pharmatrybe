"""
Work Package 1 - Phase A - Step 1
Validate the Cohort & Determine Unit of Analysis
Evidence-driven: only uses order_proc_id_coded
"""

import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Path to your CSV file
CSV_PATH = "Data/microbiology_cultures_cohort.csv"

# Connect to DuckDB (in-memory)
con = duckdb.connect("armd.db")

# Create a view for efficient querying
con.execute(f"""
    CREATE OR REPLACE VIEW cohort AS
    SELECT * FROM read_csv_auto('{CSV_PATH}')
""")

#-------------------------------------------------------------
# 1. Basic dataset info
#-------------------------------------------------------------
total_rows = con.execute("SELECT COUNT(*) FROM cohort").fetchone()[0]
columns = con.execute("DESCRIBE cohort").df()['column_name'].tolist()

print("=" * 60)
print("MICROBIOLOGY COHORT SUMMARY")
print("=" * 60)
print(f"Number of rows     : {total_rows}")
print(f"Number of columns  : {len(columns)}")
print("\nColumn names:")
for col in columns:
    print(f"  - {col}")

# Ensure the culture-order identifier exists
id_col = "order_proc_id_coded"
if id_col not in columns:
    raise ValueError(f"Column '{id_col}' not found in the dataset.")

#-------------------------------------------------------------
# 2. Total rows and distinct culture orders
#-------------------------------------------------------------
distinct_cultures = con.execute(f"SELECT COUNT(DISTINCT {id_col}) FROM cohort").fetchone()[0]
print("\n" + "=" * 60)
print("TOTAL CULTURE ORDERS")
print("=" * 60)
print(f"Total rows            : {total_rows}")
print(f"Distinct cultures     : {distinct_cultures}")
print(f"Average rows/culture  : {total_rows / distinct_cultures:.2f}")

#-------------------------------------------------------------
# 3. Rows per culture (group by culture order)
#-------------------------------------------------------------
rows_per_culture = con.execute(f"""
    SELECT {id_col}, COUNT(*) AS Rows_Per_Culture
    FROM cohort
    GROUP BY {id_col}
""").df()

#-------------------------------------------------------------
# 4. Summary statistics
#-------------------------------------------------------------
summary = rows_per_culture['Rows_Per_Culture'].describe(percentiles=[.25, .5, .75])
print("\n" + "=" * 60)
print("ROWS PER CULTURE SUMMARY")
print("=" * 60)
print(summary)
print(f"\nMaximum rows in a culture : {rows_per_culture['Rows_Per_Culture'].max()}")
print(f"Median rows per culture   : {rows_per_culture['Rows_Per_Culture'].median()}")

#-------------------------------------------------------------
# 5. Percentage with one row vs multiple rows
#-------------------------------------------------------------
pct_one = (rows_per_culture['Rows_Per_Culture'] == 1).mean() * 100
pct_mult = (rows_per_culture['Rows_Per_Culture'] > 1).mean() * 100
print(f"\nPercentage of cultures with exactly 1 row  : {pct_one:.2f}%")
print(f"Percentage of cultures with >1 row         : {pct_mult:.2f}%")

#-------------------------------------------------------------
# 6. Frequency distribution of rows per culture
#-------------------------------------------------------------
distribution = rows_per_culture['Rows_Per_Culture'].value_counts().sort_index().reset_index()
distribution.columns = ['Rows_Per_Culture', 'Count']
print("\n" + "=" * 60)
print("FREQUENCY DISTRIBUTION OF ROWS PER CULTURE")
print("=" * 60)
print(distribution.to_string(index=False))

#-------------------------------------------------------------
# 7. Top 20 cultures with the most rows
#-------------------------------------------------------------
top20 = rows_per_culture.nlargest(20, 'Rows_Per_Culture')
print("\n" + "=" * 60)
print("TOP 20 CULTURES WITH MOST ROWS")
print("=" * 60)
print(top20.to_string(index=False))

#-------------------------------------------------------------
# 8. Exact duplicate rows (using pandas)
#-------------------------------------------------------------
print("\n" + "=" * 60)
print("DUPLICATE ROWS")
print("=" * 60)

# Load entire dataset as a pandas DataFrame (only for duplicate check)
df = con.execute("SELECT * FROM cohort").df()
duplicate_count = df.duplicated().sum()
print(f"Number of exact duplicate rows : {duplicate_count}")

if duplicate_count > 0:
    dup_rows = df[df.duplicated()]
    dup_rows.to_csv("WP1_Duplicate_Records.csv", index=False)
    print("Duplicate rows written to WP1_Duplicate_Records.csv")

#-------------------------------------------------------------
# 9. Save validation tables
#-------------------------------------------------------------
distribution.to_csv("WP1_Table1_Culture_Row_Distribution.csv", index=False)
rows_per_culture.to_csv("WP1_Table2_Rows_Per_Culture.csv", index=False)
top20.to_csv("WP1_Table3_Top20_Cultures.csv", index=False)

#-------------------------------------------------------------
# 10. Histogram (capped at 15 rows)
#-------------------------------------------------------------
capped = np.minimum(rows_per_culture['Rows_Per_Culture'], 15)
plt.figure(figsize=(8,5))
plt.hist(capped, bins=np.arange(0.5, 16.5, 1), color='steelblue', edgecolor='black')
plt.title("Distribution of Rows per Culture Order (capped at 15)")
plt.xlabel("Rows per Culture")
plt.ylabel("Number of Culture Orders")
plt.xticks(range(1, 16))
plt.tight_layout()
plt.savefig("WP1_Figure1_Rows_Per_Culture.png", dpi=300)
plt.close()

#-------------------------------------------------------------
# 11. Completion message
#-------------------------------------------------------------
print("\n" + "=" * 60)
print("STEP 1 COMPLETED SUCCESSFULLY")
print("=" * 60)
print("Generated outputs:")
print("  - WP1_Table1_Culture_Row_Distribution.csv")
print("  - WP1_Table2_Rows_Per_Culture.csv")
print("  - WP1_Table3_Top20_Cultures.csv")
print("  - WP1_Figure1_Rows_Per_Culture.png")
if duplicate_count > 0:
    print("  - WP1_Duplicate_Records.csv")
print("\nValidation complete. Ready for Step 2 (aggregation).")

con.close()