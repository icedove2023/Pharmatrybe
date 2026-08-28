"""
WP2 Data Quality Audit
======================

Audits the model-ready feature table before model training.

Outputs
-------
WP2_Data_Quality_Report.csv
WP2_Data_Quality_Summary.json
WP2_Dtype_Report.csv
WP2_Missingness_Heatmap.png

This script DOES NOT modify data.
It only audits quality.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------
# Paths
# ----------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(
    PROJECT_ROOT,
    "output",
    "WP2",
    "WP2_Model_Ready_Feature_Table.parquet"
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "output",
    "WP2"
)

# ----------------------------------------------------
# Load
# ----------------------------------------------------

print("=" * 70)
print("WP2 DATA QUALITY AUDIT")
print("=" * 70)

df = pd.read_parquet(INPUT_FILE)

print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")

# ----------------------------------------------------
# Detect string NULL values
# ----------------------------------------------------

NULL_STRINGS = [
    "Null",
    "NULL",
    "null",
    "None",
    "NONE",
    ""
]

for col in df.columns:

    if df[col].dtype == object:

        df[col] = df[col].replace(NULL_STRINGS, np.nan)

# ----------------------------------------------------
# Dtype report
# ----------------------------------------------------

dtype_report = pd.DataFrame({
    "Column": df.columns,
    "Dtype": df.dtypes.astype(str)
})

dtype_report.to_csv(
    os.path.join(
        OUTPUT_DIR,
        "WP2_Dtype_Report.csv"
    ),
    index=False
)

# ----------------------------------------------------
# Per-column audit
# ----------------------------------------------------

audit = []

for col in df.columns:

    s = df[col]

    audit.append({

        "column": col,

        "dtype": str(s.dtype),

        "rows": len(s),

        "missing_count": int(s.isna().sum()),

        "missing_percent": round(
            s.isna().mean() * 100,
            2
        ),

        "unique_values": int(s.nunique(dropna=True)),

        "constant_column": bool(
            s.nunique(dropna=False) == 1
        ),

        "all_missing": bool(
            s.isna().all()
        ),

        "numeric": bool(
            pd.api.types.is_numeric_dtype(s)
        )

    })

audit = pd.DataFrame(audit)

audit = audit.sort_values(
    "missing_percent",
    ascending=False
)

audit.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "WP2_Data_Quality_Report.csv"
    ),

    index=False

)

# ----------------------------------------------------
# Numeric summary
# ----------------------------------------------------

numeric = df.select_dtypes(include=np.number)

numeric_summary = numeric.describe().T

numeric_summary.to_csv(

    os.path.join(
        OUTPUT_DIR,
        "WP2_Numeric_Summary.csv"
    )

)

# ----------------------------------------------------
# Missingness heatmap
# ----------------------------------------------------

plt.figure(figsize=(16,8))

plt.imshow(
    df.isna().T,
    aspect="auto",
    interpolation="nearest"
)

plt.xlabel("Rows")

plt.ylabel("Features")

plt.title("WP2 Missing Data Pattern")

plt.tight_layout()

plt.savefig(

    os.path.join(
        OUTPUT_DIR,
        "WP2_Missingness_Heatmap.png"
    ),

    dpi=300

)

plt.close()

# ----------------------------------------------------
# Detect suspicious columns
# ----------------------------------------------------

all_missing = audit.loc[
    audit["all_missing"],
    "column"
].tolist()

constant = audit.loc[
    audit["constant_column"],
    "column"
].tolist()

object_numeric = []

for c in df.columns:

    if df[c].dtype == object:

        try:

            pd.to_numeric(df[c])

            object_numeric.append(c)

        except:

            pass

# ----------------------------------------------------
# Summary
# ----------------------------------------------------

summary = {

    "rows": int(len(df)),

    "columns": int(len(df.columns)),

    "duplicate_rows": int(df.duplicated().sum()),

    "all_missing_columns": all_missing,

    "constant_columns": constant,

    "object_columns": df.select_dtypes(include="object").columns.tolist(),

    "object_columns_that_look_numeric": object_numeric,

    "columns_over_50_percent_missing":

        audit.loc[
            audit["missing_percent"] > 50,
            "column"
        ].tolist(),

    "columns_over_80_percent_missing":

        audit.loc[
            audit["missing_percent"] > 80,
            "column"
        ].tolist()

}

with open(

    os.path.join(
        OUTPUT_DIR,
        "WP2_Data_Quality_Summary.json"
    ),

    "w"

) as f:

    json.dump(
        summary,
        f,
        indent=4
    )

# ----------------------------------------------------
# Console report
# ----------------------------------------------------

print()

print("=" * 70)

print("AUDIT COMPLETE")

print("=" * 70)

print(f"Duplicate rows : {summary['duplicate_rows']}")

print(f"All-missing columns : {len(summary['all_missing_columns'])}")

print(f"Constant columns : {len(summary['constant_columns'])}")

print(f"Object columns : {len(summary['object_columns'])}")

print(f">50% missing : {len(summary['columns_over_50_percent_missing'])}")

print(f">80% missing : {len(summary['columns_over_80_percent_missing'])}")

print()

print("Top 20 columns with highest missingness:")

print(
    audit[
        ["column","missing_percent"]
    ].head(20)
)

print()

print("Reports written to")

print(OUTPUT_DIR)

print("=" * 70)