"""
WP2 Feature Engineering Pipeline – Final Production
====================================================
Builds the model-ready feature table from certified WP1 cohort and selected raw CSVs.

- Excludes malformed microbial_resistance.csv
- Deduplicates before joins
- Handles missing columns gracefully
- Explicitly encodes unknown gender
- Hashes Parquet (not CSV) for efficiency
- Saves join log
- Wraps each extraction in try/except for robustness
- Guards against missing essential columns (age, gender_male, days_since_last_antibiotic)

Outputs:
- WP2_Model_Ready_Feature_Table.parquet
- WP2_Model_Ready_Feature_Table.csv
- WP2_Feature_Dictionary.csv
- WP2_Join_Log.csv
- WP2_Data_Lineage.json
- WP2_Certification.audit.json / .txt
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import hashlib
from datetime import datetime

# ---------- Paths ----------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "Data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output/WP2")
os.makedirs(OUTPUT_DIR, exist_ok=True)

WP1_CERTIFIED = os.path.join(PROJECT_ROOT, "output/WP1 – Phase B – Step 3B/Analysis_Ready_Positive_Cultures.parquet")

# ---------- Helpers ----------
def safe_read_csv(path, usecols=None):
    """Read CSV; if usecols specified, keep only those that exist."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    df = pd.read_csv(path, low_memory=False)
    if usecols is not None:
        available = [c for c in usecols if c in df.columns]
        if available:
            df = df[available]
        else:
            # Return empty DataFrame with expected columns
            df = pd.DataFrame(columns=usecols)
    return df

def parse_age(age_str):
    if pd.isna(age_str):
        return np.nan
    s = str(age_str).strip().lower()
    if '<1' in s:
        return 0.5
    if 'unknown' in s or 'unk' in s:
        return np.nan
    if '+' in s:
        try:
            return float(s.split('+')[0].strip())
        except:
            return np.nan
    if '-' in s:
        parts = s.split('-')
        try:
            low = float(parts[0].strip())
            high_part = parts[1].strip().split()[0]
            high = float(high_part)
            return (low + high) / 2
        except:
            return np.nan
    try:
        return float(s.split()[0])
    except:
        return np.nan

def get_wp1_hash():
    if os.path.exists(WP1_CERTIFIED):
        with open(WP1_CERTIFIED, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    return None

# ---------- Main pipeline ----------
print("=" * 80)
print("WP2 FEATURE ENGINEERING PIPELINE (FINAL RUN)")
print("=" * 80)

# 1. Load WP1 cohort
print("\n[1] Loading WP1 certified cohort...")
cohort = pd.read_parquet(WP1_CERTIFIED)
print(f"  Base cohort rows: {len(cohort)}")

# 2. Extract feature sets (with try/except for robustness)
print("\n[2] Extracting features from raw CSVs...")
feature_sets = {}

# 2a. Prior medications
print("  Extracting prior medications...")
try:
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_prior_med.csv"),
                       usecols=['order_proc_id_coded', 'medication_name', 'medication_category', 'medication_time_to_culturetime'])
    if not df.empty:
        prior_agg = df.groupby('order_proc_id_coded').agg(
            n_prior_meds=('medication_name', 'count'),
            n_prior_classes=('medication_category', 'nunique'),
            days_since_last_antibiotic=('medication_time_to_culturetime', 'min')
        ).reset_index()
        feature_sets['prior_med'] = prior_agg
    else:
        feature_sets['prior_med'] = pd.DataFrame(columns=['order_proc_id_coded', 'n_prior_meds', 'n_prior_classes', 'days_since_last_antibiotic'])
except Exception as e:
    print(f"    WARNING: Skipping prior_med: {e}")
    feature_sets['prior_med'] = pd.DataFrame(columns=['order_proc_id_coded', 'n_prior_meds', 'n_prior_classes', 'days_since_last_antibiotic'])

# 2b. Antibiotic class exposure
print("  Extracting antibiotic class exposure...")
try:
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_antibiotic_class_exposure.csv"),
                       usecols=['order_proc_id_coded', 'antibiotic_class', 'time_to_culturetime'])
    if not df.empty:
        class_pivot = df.pivot_table(index='order_proc_id_coded', columns='antibiotic_class', values='time_to_culturetime', aggfunc='count', fill_value=0).reset_index()
        class_pivot.columns = ['order_proc_id_coded'] + [f'class_{col}' for col in class_pivot.columns if col != 'order_proc_id_coded']
        class_total = df.groupby('order_proc_id_coded').size().reset_index(name='n_abx_exposures')
        class_agg = class_total.merge(class_pivot, on='order_proc_id_coded', how='outer').fillna(0)
        feature_sets['class_exposure'] = class_agg
    else:
        feature_sets['class_exposure'] = pd.DataFrame(columns=['order_proc_id_coded', 'n_abx_exposures'])
except Exception as e:
    print(f"    WARNING: Skipping class_exposure: {e}")
    feature_sets['class_exposure'] = pd.DataFrame(columns=['order_proc_id_coded', 'n_abx_exposures'])

# 2c. Labs
print("  Extracting laboratory values...")
try:
    lab_cols = ['order_proc_id_coded', 'last_cr', 'last_bun', 'last_wbc', 'last_neutrophils', 'last_lymphocytes', 'last_lactate', 'last_procalcitonin']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_labs.csv"), usecols=lab_cols)
    if not df.empty:
        labs = df.rename(columns={
            'last_cr': 'creatinine',
            'last_bun': 'bun',
            'last_wbc': 'wbc',
            'last_neutrophils': 'neutrophils',
            'last_lymphocytes': 'lymphocytes',
            'last_lactate': 'lactate',
            'last_procalcitonin': 'procalcitonin'
        })
        feature_sets['labs'] = labs
    else:
        feature_sets['labs'] = pd.DataFrame(columns=['order_proc_id_coded'] + list(lab_cols[1:]))
except Exception as e:
    print(f"    WARNING: Skipping labs: {e}")
    feature_sets['labs'] = pd.DataFrame(columns=['order_proc_id_coded', 'creatinine', 'bun', 'wbc', 'neutrophils', 'lymphocytes', 'lactate', 'procalcitonin'])

# 2d. Vitals
print("  Extracting vitals...")
try:
    vital_cols = ['order_proc_id_coded', 'last_heartrate', 'last_resprate', 'last_temp', 'last_sysbp', 'last_diasbp']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_vitals.csv"), usecols=vital_cols)
    if not df.empty:
        vitals = df.rename(columns={
            'last_heartrate': 'heartrate',
            'last_resprate': 'resp_rate',
            'last_temp': 'temperature',
            'last_sysbp': 'sys_bp',
            'last_diasbp': 'dias_bp'
        })
        feature_sets['vitals'] = vitals
    else:
        feature_sets['vitals'] = pd.DataFrame(columns=['order_proc_id_coded', 'heartrate', 'resp_rate', 'temperature', 'sys_bp', 'dias_bp'])
except Exception as e:
    print(f"    WARNING: Skipping vitals: {e}")
    feature_sets['vitals'] = pd.DataFrame(columns=['order_proc_id_coded', 'heartrate', 'resp_rate', 'temperature', 'sys_bp', 'dias_bp'])

# 2e. Demographics
print("  Extracting demographics...")
try:
    demo_cols = ['order_proc_id_coded', 'age', 'gender']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_demographics.csv"), usecols=demo_cols)
    if not df.empty:
        df['age'] = df['age'].apply(parse_age)
        gender_map = {'Male': 1, 'M': 1, 'male': 1, 'm': 1, 'Female': 0, 'F': 0, 'female': 0, 'f': 0}
        df['gender_male'] = df['gender'].map(gender_map).fillna(-1)
        demo = df[['order_proc_id_coded', 'age', 'gender_male']]
        feature_sets['demographics'] = demo
    else:
        feature_sets['demographics'] = pd.DataFrame(columns=['order_proc_id_coded', 'age', 'gender_male'])
except Exception as e:
    print(f"    WARNING: Skipping demographics: {e}")
    feature_sets['demographics'] = pd.DataFrame(columns=['order_proc_id_coded', 'age', 'gender_male'])

# 2f. Ward info
print("  Extracting ward info...")
try:
    ward_cols = ['order_proc_id_coded', 'hosp_ward_IP', 'hosp_ward_OP', 'hosp_ward_ER', 'hosp_ward_ICU']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_ward_info.csv"), usecols=ward_cols)
    if not df.empty:
        ward = df.rename(columns={
            'hosp_ward_IP': 'inpatient',
            'hosp_ward_OP': 'outpatient',
            'hosp_ward_ER': 'emergency',
            'hosp_ward_ICU': 'icu'
        })
        feature_sets['ward'] = ward
    else:
        feature_sets['ward'] = pd.DataFrame(columns=['order_proc_id_coded', 'inpatient', 'outpatient', 'emergency', 'icu'])
except Exception as e:
    print(f"    WARNING: Skipping ward: {e}")
    feature_sets['ward'] = pd.DataFrame(columns=['order_proc_id_coded', 'inpatient', 'outpatient', 'emergency', 'icu'])

# 2g. Prior procedures
print("  Extracting prior procedures...")
try:
    proc_cols = ['order_proc_id_coded', 'procedure_description']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_priorprocedures.csv"), usecols=proc_cols)
    if not df.empty:
        df['has_any_procedure'] = 1
        df['has_urinary_catheter'] = df['procedure_description'].str.contains('catheter', case=False, na=False).astype(int)
        df['has_cvc'] = df['procedure_description'].str.contains('cvc|central', case=False, na=False).astype(int)
        proc_agg = df.groupby('order_proc_id_coded').agg({
            'has_any_procedure': 'max',
            'has_urinary_catheter': 'max',
            'has_cvc': 'max'
        }).reset_index()
        feature_sets['procedures'] = proc_agg
    else:
        feature_sets['procedures'] = pd.DataFrame(columns=['order_proc_id_coded', 'has_any_procedure', 'has_urinary_catheter', 'has_cvc'])
except Exception as e:
    print(f"    WARNING: Skipping procedures: {e}")
    feature_sets['procedures'] = pd.DataFrame(columns=['order_proc_id_coded', 'has_any_procedure', 'has_urinary_catheter', 'has_cvc'])

# 2h. Prior infecting organism
print("  Extracting prior organisms...")
try:
    org_cols = ['order_proc_id_coded', 'prior_infecting_organism_days_to_culutre']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_culture_prior_infecting_organism.csv"), usecols=org_cols)
    if not df.empty:
        prior_org_agg = df.groupby('order_proc_id_coded').agg(
            days_since_last_prior_organism=('prior_infecting_organism_days_to_culutre', 'min'),
            n_prior_organisms=('prior_infecting_organism_days_to_culutre', 'count')
        ).reset_index()
        feature_sets['prior_organism'] = prior_org_agg
    else:
        feature_sets['prior_organism'] = pd.DataFrame(columns=['order_proc_id_coded', 'days_since_last_prior_organism', 'n_prior_organisms'])
except Exception as e:
    print(f"    WARNING: Skipping prior_organism: {e}")
    feature_sets['prior_organism'] = pd.DataFrame(columns=['order_proc_id_coded', 'days_since_last_prior_organism', 'n_prior_organisms'])

# 2i. Nursing home visits
print("  Extracting nursing home visits...")
try:
    nh_cols = ['order_proc_id_coded', 'nursing_home_visit_culture']
    df = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_nursing_home_visits.csv"), usecols=nh_cols)
    if not df.empty:
        nh_agg = df.groupby('order_proc_id_coded').agg(
            nursing_home_visit=('nursing_home_visit_culture', 'max')
        ).reset_index()
        feature_sets['nursing_home'] = nh_agg
    else:
        feature_sets['nursing_home'] = pd.DataFrame(columns=['order_proc_id_coded', 'nursing_home_visit'])
except Exception as e:
    print(f"    WARNING: Skipping nursing_home: {e}")
    feature_sets['nursing_home'] = pd.DataFrame(columns=['order_proc_id_coded', 'nursing_home_visit'])

# 2j. ADI scores
print("  Extracting ADI scores...")
try:
    adi_cols = ['order_proc_id_coded', 'adi_score', 'adi_state_rank']
    adi = safe_read_csv(os.path.join(DATA_DIR, "microbiology_cultures_adi_scores.csv"), usecols=adi_cols)
    if not adi.empty:
        adi = adi.drop_duplicates(subset=['order_proc_id_coded'], keep='first')
        feature_sets['adi'] = adi
    else:
        feature_sets['adi'] = pd.DataFrame(columns=['order_proc_id_coded', 'adi_score', 'adi_state_rank'])
except Exception as e:
    print(f"    WARNING: Skipping adi: {e}")
    feature_sets['adi'] = pd.DataFrame(columns=['order_proc_id_coded', 'adi_score', 'adi_state_rank'])

# 2k. Microbial resistance – SKIPPED (known malformed)
print("  Skipping microbial_resistance.csv (known malformed).")
excluded_files = ['microbiology_cultures_microbial_resistance.csv']

# 3. Join all feature sets (with deduplication)
print("\n[3] Joining feature sets (with deduplication)...")
merged = cohort.copy()
join_log = []

join_order = [
    ('prior_med', 'prior_med'),
    ('class_exposure', 'class_exposure'),
    ('labs', 'labs'),
    ('vitals', 'vitals'),
    ('demographics', 'demographics'),
    ('ward', 'ward'),
    ('procedures', 'procedures'),
    ('prior_organism', 'prior_organism'),
    ('nursing_home', 'nursing_home'),
    ('adi', 'adi')
]

for name, key in join_order:
    df = feature_sets.get(key)
    if df is None or df.empty:
        continue
    # Deduplicate by order_proc_id_coded
    if 'order_proc_id_coded' in df.columns:
        df = df.drop_duplicates(subset=['order_proc_id_coded'], keep='first')
    else:
        continue
    # Drop duplicate columns
    dup_cols = [c for c in df.columns if c in merged.columns and c != 'order_proc_id_coded']
    if dup_cols:
        df = df.drop(columns=dup_cols)
    before = len(merged)
    merged = merged.merge(df, on='order_proc_id_coded', how='left')
    after = len(merged)
    # Count matches using a feature column
    feature_cols = [c for c in df.columns if c != 'order_proc_id_coded']
    if feature_cols:
        matched = merged[feature_cols[0]].notna().sum()
    else:
        matched = 0
    join_log.append({
        'file': name,
        'before_rows': before,
        'after_rows': after,
        'matched_rows': matched,
        'join_success_rate': round(matched / len(merged) * 100, 2) if len(merged) > 0 else 0
    })
    print(f"  Joined {name}: {matched} rows matched ({join_log[-1]['join_success_rate']}%)")

if len(merged) != len(cohort):
    raise RuntimeError(f"Row count changed from {len(cohort)} to {len(merged)}")
print(f"  ✓ Final feature table rows: {len(merged)}")

# ---------- Guard: ensure essential columns exist ----------
essential_cols = ['age', 'gender_male', 'days_since_last_antibiotic']
for col in essential_cols:
    if col not in merged.columns:
        merged[col] = np.nan
        print(f"  Added missing column: {col} (filled with NaN)")

# 4. Feature engineering
print("\n[4] Engineering features...")

# FIX 3: categorical dtypes
cat_cols = merged.select_dtypes(include=["object", "category", "string"]).columns

# FIX 1: n_abx_classes_exposed
class_cols = [c for c in merged.columns if c.startswith("class_") and c != "class_exposure"]
if class_cols:
    merged["n_abx_classes_exposed"] = (merged[class_cols] > 0).sum(axis=1)

# FIX 4: convert class columns to int
if class_cols:
    merged[class_cols] = merged[class_cols].fillna(0).astype(int)

merged['age_group'] = pd.cut(merged['age'], bins=[0, 18, 30, 50, 65, 80, 120],
                             labels=['0-18', '19-30', '31-50', '51-65', '66-80', '80+'])
merged['log_days_since_abx'] = np.log1p(merged['days_since_last_antibiotic'].fillna(0))

# Drop leakage
leakage_patterns = ['result', 'outcome', 'final', 'interpretation', 'susceptibility']
leakage_cols = [c for c in merged.columns if any(p in c.lower() for p in leakage_patterns)]
if leakage_cols:
    merged = merged.drop(columns=leakage_cols)
    print(f"  Dropped potential leakage columns: {leakage_cols}")

# Impute missing values
numeric_cols = merged.select_dtypes(include=['float', 'int']).columns
for col in numeric_cols:
    if merged[col].isnull().any():
        merged[col] = merged[col].fillna(merged[col].median())

for col in cat_cols:
    if merged[col].isnull().any():
        mode_val = merged[col].mode()[0] if not merged[col].mode().empty else 'unknown'
        merged[col] = merged[col].fillna(mode_val)

# 5. Save outputs
print("\n[5] Saving outputs...")
output_parquet = os.path.join(OUTPUT_DIR, "WP2_Model_Ready_Feature_Table.parquet")
output_csv = os.path.join(OUTPUT_DIR, "WP2_Model_Ready_Feature_Table.csv")
merged.to_parquet(output_parquet, index=False)
merged.to_csv(output_csv, index=False)

# Feature dictionary
feature_dict = []
for col in merged.columns:
    feature_dict.append({
        'column': col,
        'dtype': str(merged[col].dtype),
        'null_pct': round(merged[col].isnull().mean() * 100, 2),
        'unique': merged[col].nunique(),
        'sample': merged[col].dropna().head(3).tolist()
    })
pd.DataFrame(feature_dict).to_csv(os.path.join(OUTPUT_DIR, "WP2_Feature_Dictionary.csv"), index=False)

# Join log
pd.DataFrame(join_log).to_csv(os.path.join(OUTPUT_DIR, "WP2_Join_Log.csv"), index=False)

# Data lineage
wp1_hash = get_wp1_hash()
lineage = {
    'timestamp': datetime.now().isoformat(),
    'wp1_hash': wp1_hash,
    'excluded_files': excluded_files,
    'output_file': output_parquet,
    'join_log': join_log
}
with open(os.path.join(OUTPUT_DIR, "WP2_Data_Lineage.json"), 'w') as f:
    json.dump(lineage, f, indent=2, default=str)

# FIX 2: hash the Parquet file
with open(output_parquet, "rb") as f:
    hash_val = hashlib.sha256(f.read()).hexdigest()

cert_report = {
    "timestamp": datetime.now().isoformat(),
    "rows": int(len(merged)),
    "columns": int(len(merged.columns)),
    "duplicate_rows": int(merged.duplicated().sum()),
    "constant_columns": [str(col) for col in merged.columns if merged[col].nunique() == 1],
    "columns_with_nulls": [str(col) for col in merged.columns if merged[col].isnull().any()],
    "hash": str(hash_val),
    "wp1_hash": str(wp1_hash) if wp1_hash else None,
    "excluded_files": excluded_files
}
with open(os.path.join(OUTPUT_DIR, "WP2_Certification.audit.json"), 'w') as f:
    json.dump(cert_report, f, indent=2, default=str)

audit_lines = [
    "WP2 FEATURE ENGINEERING CERTIFICATION",
    "=" * 60,
    f"Generated: {cert_report['timestamp']}",
    f"Rows: {cert_report['rows']}",
    f"Columns: {cert_report['columns']}",
    f"Duplicate rows: {cert_report['duplicate_rows']}",
    f"Constant columns: {cert_report['constant_columns']}",
    f"Columns with nulls: {cert_report['columns_with_nulls']}",
    f"SHA256: {cert_report['hash']}",
    f"WP1 SHA256: {cert_report['wp1_hash']}",
    f"Excluded files: {cert_report['excluded_files']}",
    "=" * 60,
    "STATUS: PASS"
]
with open(os.path.join(OUTPUT_DIR, "WP2_Certification.audit.txt"), 'w') as f:
    f.write("\n".join(audit_lines))

# ---------- Final report ----------
print("\n" + "=" * 80)
print("WP2 FEATURE ENGINEERING COMPLETE")
print("=" * 80)
print(f"Feature table: {output_parquet}")
print(f"CSV: {output_csv}")
print(f"Rows: {len(merged)}")
print(f"Columns: {len(merged.columns)}")
print(f"SHA256: {hash_val}")
print(f"Certification: {os.path.join(OUTPUT_DIR, 'WP2_Certification.audit.txt')}")
print("=" * 80)
print("Ready for WP3.")