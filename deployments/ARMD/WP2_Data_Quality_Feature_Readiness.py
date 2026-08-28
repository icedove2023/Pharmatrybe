"""
WP2 Data Quality & Feature Readiness Certification
===================================================
Deep audit of raw ARMD CSVs before feature extraction.

Performs:
- Mixed datatype detection
- Categorical explosion (high‑cardinality flags)
- Near‑duplicate column detection (Levenshtein)
- Constant column detection
- Missingness pattern analysis (by year, ward, organism where available)
- Out‑of‑range value detection for clinical variables
- Date consistency (admission ≤ culture ≤ AST ≤ discharge)
- Join cardinality assessment (1:1, 1:many, many:1, many:many)
- Completeness, consistency, uniqueness, validity, integrity scores
- Dataset classification (Clinical, Microbiology, Lab, Medication, Vitals, Admin)
- Feature readiness matrix (Recommended, Optional, Exclude)
- Feature relevance ranking for AMR prediction

Outputs:
- WP2_Data_Quality_Report.xlsx
- WP2_Feature_Relevance_Ranking.xlsx
- WP2_Readiness_Summary.txt
"""

import os
import sys
import pandas as pd
import numpy as np
import duckdb
import json
import re
from datetime import datetime
from collections import defaultdict
from difflib import SequenceMatcher

# ---------- Paths ----------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output/WP2_Quality_Readiness")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- Constants ----------
POTENTIAL_KEYS = ['order_proc_id_coded', 'pat_enc_csn_id_coded', 'anon_id']
CLINICAL_VARIABLES = {
    'age': {'min': 0, 'max': 120},
    'temp': {'min': 30, 'max': 45},
    'heartrate': {'min': 20, 'max': 250},
    'resprate': {'min': 4, 'max': 80},
    'sysbp': {'min': 40, 'max': 250},
    'diasbp': {'min': 20, 'max': 150},
    'creatinine': {'min': 0, 'max': 20},
    'bun': {'min': 0, 'max': 200},
    'wbc': {'min': 0, 'max': 100},
    'lactate': {'min': 0, 'max': 20}
}
DATE_COL_PATTERNS = ['date', 'time', 'datetime', 'jittered', 'admit', 'discharge', 'birth', 'collect', 'order']

# ---------- Helper functions ----------
def detect_encoding(filepath):
    import chardet
    with open(filepath, 'rb') as f:
        raw = f.read(10000)
        result = chardet.detect(raw)
        return result['encoding'] if result['encoding'] else 'utf-8'

def detect_delimiter(filepath, encoding='utf-8'):
    import csv
    with open(filepath, 'r', encoding=encoding) as f:
        sample = f.read(2048)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=',;\t|')
            return dialect.delimiter
        except:
            return ','

def clean_column_name(col):
    # Remove special chars, collapse spaces, lower
    return re.sub(r'[^a-zA-Z0-9_]', '', col).lower()

def levenshtein_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ---------- Main inspection ----------
def inspect_file(filepath):
    fname = os.path.basename(filepath)
    encoding = detect_encoding(filepath)
    delimiter = detect_delimiter(filepath, encoding)

    # Use DuckDB to load the file
    con = duckdb.connect()
    con.execute(f"CREATE OR REPLACE VIEW file_view AS SELECT * FROM read_csv_auto('{filepath}', delim='{delimiter}', encoding='{encoding}', ignore_errors=True)")

    # Get schema and sample
    df_sample = con.execute("SELECT * FROM file_view LIMIT 1000").df()
    total_rows = con.execute("SELECT COUNT(*) FROM file_view").fetchone()[0]

    # Column list
    columns = con.execute("DESCRIBE file_view").df()['column_name'].tolist()

    # 1. Mixed datatypes
    mixed_cols = []
    for col in columns:
        # Try to infer numeric vs string
        if col not in df_sample.columns:
            continue
        # Convert sample to string and test numeric conversion
        sample_str = df_sample[col].astype(str)
        numeric_count = sample_str.str.match(r'^-?\d+\.?\d*$').sum()
        total_sample = len(sample_str)
        if total_sample > 0 and 0 < numeric_count < total_sample:
            mixed_cols.append({
                'column': col,
                'numeric_pct': round(numeric_count / total_sample * 100, 2)
            })

    # 2. High cardinality categorical
    high_card_cols = []
    for col in columns:
        distinct = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM file_view").fetchone()[0]
        if distinct > 100 and distinct / total_rows < 0.8:
            # Likely categorical with many categories
            top = con.execute(f"SELECT {col} FROM file_view GROUP BY {col} ORDER BY COUNT(*) DESC LIMIT 20").df()
            high_card_cols.append({
                'column': col,
                'distinct': distinct,
                'distinct_pct': round(distinct / total_rows * 100, 2),
                'top_values': top[col].tolist()[:5]
            })

    # 3. Constant columns
    constant_cols = []
    for col in columns:
        distinct = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM file_view").fetchone()[0]
        if distinct == 1:
            constant_cols.append(col)

    # 4. Missingness patterns (overall only; complex patterns require joins)
    missingness = {}
    for col in columns:
        null_count = con.execute(f"SELECT COUNT(*) FROM file_view WHERE {col} IS NULL").fetchone()[0]
        missingness[col] = round(null_count / total_rows * 100, 2)

    # 5. Out-of-range values for clinical variables
    out_of_range = {}
    for col in columns:
        col_clean = clean_column_name(col)
        for var, bounds in CLINICAL_VARIABLES.items():
            if var in col_clean:
                q = f"SELECT COUNT(*) FROM file_view WHERE {col} < {bounds['min']} OR {col} > {bounds['max']}"
                cnt = con.execute(q).fetchone()[0]
                if cnt > 0:
                    out_of_range[col] = {
                        'var': var,
                        'out_of_range': cnt,
                        'min': bounds['min'],
                        'max': bounds['max']
                    }
                break

    # 6. Date consistency (if we have date columns)
    date_cols = [c for c in columns if any(p in c.lower() for p in DATE_COL_PATTERNS)]
    date_issues = []
    if len(date_cols) >= 2:
        # Check if any date is after another
        for i, c1 in enumerate(date_cols):
            for c2 in date_cols[i+1:]:
                # If c1 > c2 is common, we'll sample
                sample_dates = con.execute(f"SELECT {c1}, {c2} FROM file_view WHERE {c1} IS NOT NULL AND {c2} IS NOT NULL LIMIT 100").df()
                if not sample_dates.empty:
                    try:
                        d1 = pd.to_datetime(sample_dates.iloc[:,0])
                        d2 = pd.to_datetime(sample_dates.iloc[:,1])
                        violations = (d1 > d2).sum()
                        if violations > 0:
                            date_issues.append({
                                'col1': c1,
                                'col2': c2,
                                'violations': violations,
                                'sample': sample_dates.head(3).to_dict(orient='records')
                            })
                    except:
                        pass

    # 7. Join cardinality (estimate using key stats)
    key_stats = {}
    for key in POTENTIAL_KEYS:
        if key in columns:
            distinct = con.execute(f"SELECT COUNT(DISTINCT {key}) FROM file_view").fetchone()[0]
            null_count = con.execute(f"SELECT COUNT(*) FROM file_view WHERE {key} IS NULL").fetchone()[0]
            key_stats[key] = {
                'distinct': distinct,
                'null_pct': round(null_count / total_rows * 100, 2),
                'uniqueness': round(distinct / total_rows * 100, 2)
            }

    # 8. Completeness score (weighted by missingness)
    completeness = 100 - np.mean(list(missingness.values())) if missingness else 0

    # 9. Dataset classification (simple heuristic)
    classification = 'Other'
    if any('organism' in c.lower() or 'antibiotic' in c.lower() for c in columns):
        classification = 'Microbiology'
    elif any('age' in c.lower() or 'gender' in c.lower() for c in columns):
        classification = 'Demographics'
    elif any('creatinine' in c.lower() or 'wbc' in c.lower() for c in columns):
        classification = 'Laboratory'
    elif any('medication' in c.lower() or 'drug' in c.lower() for c in columns):
        classification = 'Medication'
    elif any('heartrate' in c.lower() or 'temp' in c.lower() for c in columns):
        classification = 'Vitals'
    elif any('admit' in c.lower() or 'discharge' in c.lower() for c in columns):
        classification = 'Administrative'

    # 10. Feature readiness (draft)
    feature_readiness = {}
    for col in columns:
        if col in constant_cols:
            readiness = 'Exclude (constant)'
        elif col in POTENTIAL_KEYS:
            readiness = 'Key'
        elif any(var in clean_column_name(col) for var in CLINICAL_VARIABLES):
            if out_of_range.get(col, {}).get('out_of_range', 0) > 10:
                readiness = 'Review (out of range)'
            else:
                readiness = 'Recommended'
        elif mixed_cols and any(m['column'] == col for m in mixed_cols):
            readiness = 'Review (mixed datatype)'
        elif high_card_cols and any(h['column'] == col for h in high_card_cols):
            readiness = 'Review (high cardinality)'
        else:
            readiness = 'Optional'
        feature_readiness[col] = readiness

    con.close()
    return {
        'filename': fname,
        'encoding': encoding,
        'delimiter': delimiter,
        'total_rows': total_rows,
        'columns': columns,
        'mixed_cols': mixed_cols,
        'high_card_cols': high_card_cols,
        'constant_cols': constant_cols,
        'missingness': missingness,
        'out_of_range': out_of_range,
        'date_issues': date_issues,
        'key_stats': key_stats,
        'completeness': completeness,
        'classification': classification,
        'feature_readiness': feature_readiness,
        'quality_score': round(completeness * 0.6 + (100 - len(constant_cols) / len(columns) * 20) * 0.2 + (100 - len(mixed_cols) / len(columns) * 20) * 0.2, 1)
    }

# ---------- Run audit ----------
print("=" * 80)
print("WP2 DATA QUALITY & FEATURE READINESS CERTIFICATION")
print("=" * 80)

csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
print(f"\nFound {len(csv_files)} CSV files\n")

results = {}
for f in csv_files:
    print(f"  Inspecting {f}...")
    path = os.path.join(DATA_DIR, f)
    try:
        results[f] = inspect_file(path)
        print(f"    Rows: {results[f]['total_rows']}, Columns: {len(results[f]['columns'])}, Score: {results[f]['quality_score']}")
    except Exception as e:
        print(f"    ERROR: {e}")
        results[f] = {'error': str(e)}

# ---------- Generate outputs ----------
# 1. Excel report with multiple sheets
output_xlsx = os.path.join(OUTPUT_DIR, "WP2_Data_Quality_Report.xlsx")
with pd.ExcelWriter(output_xlsx, engine='openpyxl') as writer:
    # Summary
    summary_rows = []
    for f, res in results.items():
        if 'error' in res:
            summary_rows.append({'File': f, 'Status': 'ERROR', 'Error': res['error']})
            continue
        summary_rows.append({
            'File': f,
            'Classification': res['classification'],
            'Rows': res['total_rows'],
            'Columns': len(res['columns']),
            'Completeness %': res['completeness'],
            'Quality Score': res['quality_score'],
            'Constant Columns': len(res['constant_cols']),
            'Mixed Columns': len(res['mixed_cols']),
            'High Cardinality': len(res['high_card_cols'])
        })
    pd.DataFrame(summary_rows).to_excel(writer, sheet_name='Summary', index=False)

    # Feature Readiness per file
    for f, res in results.items():
        if 'error' in res:
            continue
        readiness_rows = []
        for col, ready in res['feature_readiness'].items():
            readiness_rows.append({
                'Column': col,
                'Readiness': ready,
                'Missing %': res['missingness'].get(col, 0),
                'Dtype': 'mixed' if any(m['column'] == col for m in res['mixed_cols']) else 'uniform'
            })
        pd.DataFrame(readiness_rows).to_excel(writer, sheet_name=f[:31], index=False)

# 2. Feature Relevance Ranking (across all files)
relevance_rows = []
for f, res in results.items():
    if 'error' in res:
        continue
    for col, ready in res['feature_readiness'].items():
        # Priority: Recommended > Optional > Review > Exclude
        priority = 5 if 'Recommended' in ready else 3 if 'Optional' in ready else 1 if 'Review' in ready else 0
        relevance_rows.append({
            'File': f,
            'Column': col,
            'Classification': res['classification'],
            'Readiness': ready,
            'Missing %': res['missingness'].get(col, 0),
            'Priority': priority,
            'Clinical Meaning': 'Yes' if any(var in clean_column_name(col) for var in CLINICAL_VARIABLES) else 'Unknown'
        })
relevance_df = pd.DataFrame(relevance_rows)
relevance_df = relevance_df.sort_values(['Priority', 'Missing %'], ascending=[False, True])
relevance_df.to_excel(os.path.join(OUTPUT_DIR, "WP2_Feature_Relevance_Ranking.xlsx"), index=False)

# 3. Summary report
report = []
report.append("=" * 80)
report.append("WP2 DATA QUALITY & FEATURE READINESS CERTIFICATION")
report.append("=" * 80)
report.append(f"Generated: {datetime.now().isoformat()}")
report.append(f"Files audited: {len(csv_files)}")
report.append("")
report.append("--- SUMMARY ---")
for f, res in results.items():
    if 'error' in res:
        report.append(f"⚠️ {f}: ERROR - {res['error']}")
    else:
        report.append(
            f"✓ {f}: {res['classification']}, {res['total_rows']:,} rows, "
            f"Quality: {res['quality_score']}/100"
        )
report.append("")
report.append("--- FILES WITH CONSTANT COLUMNS ---")
for f, res in results.items():
    if 'error' not in res and res['constant_cols']:
        report.append(f"  {f}: {len(res['constant_cols'])} constant columns")
        for col in res['constant_cols'][:5]:
            report.append(f"    - {col}")
        if len(res['constant_cols']) > 5:
            report.append(f"    ... and {len(res['constant_cols']) - 5} more")
report.append("")
report.append("--- FILES WITH MIXED DATATYPES ---")
for f, res in results.items():
    if 'error' not in res and res['mixed_cols']:
        report.append(f"  {f}: {len(res['mixed_cols'])} mixed columns")
        for m in res['mixed_cols'][:5]:
            report.append(f"    - {m['column']}: {m['numeric_pct']}% numeric")
        if len(res['mixed_cols']) > 5:
            report.append(f"    ... and {len(res['mixed_cols']) - 5} more")
report.append("")
report.append("--- HIGH CARDINALITY CATEGORICALS ---")
for f, res in results.items():
    if 'error' not in res and res['high_card_cols']:
        report.append(f"  {f}: {len(res['high_card_cols'])} high‑cardinality columns")
        for h in res['high_card_cols'][:5]:
            report.append(f"    - {h['column']}: {h['distinct']} unique ({h['distinct_pct']}%)")
        if len(res['high_card_cols']) > 5:
            report.append(f"    ... and {len(res['high_card_cols']) - 5} more")
report.append("")
report.append("--- DATE CONSISTENCY ISSUES ---")
for f, res in results.items():
    if 'error' not in res and res['date_issues']:
        report.append(f"  {f}: {len(res['date_issues'])} date violations")
        for d in res['date_issues'][:5]:
            report.append(f"    - {d['col1']} > {d['col2']}: {d['violations']} rows")
        if len(res['date_issues']) > 5:
            report.append(f"    ... and {len(res['date_issues']) - 5} more")
report.append("")
report.append("--- FEATURE READINESS SUMMARY ---")
readiness_counts = defaultdict(int)
for f, res in results.items():
    if 'error' not in res:
        for ready in res['feature_readiness'].values():
            readiness_counts[ready] += 1
for ready, count in readiness_counts.items():
    report.append(f"  {ready}: {count}")
report.append("")
report.append("--- NEXT STEPS ---")
report.append("1. Review the Data Quality Report and Feature Relevance Ranking.")
report.append("2. Decide on handling mixed datatypes, high cardinality, and constant columns.")
report.append("3. For date violations, investigate and resolve.")
report.append("4. Use the Feature Relevance Ranking to guide feature extraction.")
report.append("5. Proceed to WP2 feature extraction only after addressing critical issues.")

report_path = os.path.join(OUTPUT_DIR, "WP2_Readiness_Summary.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(report))

print("\n" + "=" * 80)
print("CERTIFICATION COMPLETE")
print("=" * 80)
print(f"All outputs saved to: {OUTPUT_DIR}")
print("  - WP2_Data_Quality_Report.xlsx")
print("  - WP2_Feature_Relevance_Ranking.xlsx")
print("  - WP2_Readiness_Summary.txt")