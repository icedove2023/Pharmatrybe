-- =================================================================
-- SQL Schema for WHO Respiratory CDSS Knowledge Base
--
-- Target: PostgreSQL 16+
-- Version: 2.1 (with normalized drugs)
-- =================================================================

BEGIN;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS recommendation_pathogens, disease_pathogens, recommendations, evidence, referral, follow_up, monitoring, stewardship, diagnostics, drugs, pathogens, diseases, metadata CASCADE;

-- =================================================================
-- METADATA
-- =================================================================
CREATE TABLE metadata (
    metadata_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    version TEXT,
    normalization_version TEXT,
    created_at TIMESTAMPTZ,
    disease_count INTEGER,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE metadata IS 'High-level metadata for each knowledge base import.';

-- =================================================================
-- DISEASES
-- =================================================================
CREATE TABLE diseases (
    disease_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    chapter_number INTEGER,
    chapter_title TEXT,
    care_level TEXT,
    description TEXT,
    source_pages INTEGER[]
);
COMMENT ON TABLE diseases IS 'Core table for disease definitions.';
CREATE INDEX idx_diseases_name ON diseases(name);

-- =================================================================
-- PATHOGENS
-- =================================================================
CREATE TABLE pathogens (
    pathogen_id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
COMMENT ON TABLE pathogens IS 'Normalized master list of all unique pathogens.';

-- =================================================================
-- DRUGS
-- =================================================================
CREATE TABLE drugs (
    drug_id TEXT PRIMARY KEY,
    generic_name TEXT NOT NULL UNIQUE,
    aware_group TEXT,
    antibiotic_class TEXT,
    route TEXT,
    notes TEXT,
    CHECK (aware_group IN ('Access', 'Watch', 'Reserve'))
);
COMMENT ON TABLE drugs IS 'Normalized master list of all unique drugs.';
CREATE INDEX idx_drugs_generic_name ON drugs(generic_name);
CREATE INDEX idx_drugs_aware_group ON drugs(aware_group);

-- =================================================================
-- EVIDENCE (UNIQUE constraint removed from text)
-- =================================================================
CREATE TABLE evidence (
    evidence_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    type TEXT,
    text TEXT NOT NULL,   -- UNIQUE removed (same text can appear for multiple diseases)
    page INTEGER
);
COMMENT ON TABLE evidence IS 'Stores evidence statements, which may be repeated across diseases.';
CREATE INDEX idx_evidence_disease_id ON evidence(disease_id);
CREATE INDEX idx_evidence_type ON evidence(type);
-- Optional full‑text search index for later use:
-- CREATE INDEX idx_evidence_text_gin ON evidence USING GIN (to_tsvector('english', text));

-- =================================================================
-- RECOMMENDATIONS
-- =================================================================
CREATE TABLE recommendations (
    recommendation_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    evidence_id TEXT REFERENCES evidence(evidence_id) ON DELETE SET NULL,
    drug_id TEXT REFERENCES drugs(drug_id) ON DELETE RESTRICT,

    recommendation_type TEXT,
    population TEXT,
    severity TEXT,
    source_page INTEGER CHECK (source_page > 0),

    dose_raw TEXT,
    dose_value_min NUMERIC,
    dose_value_max NUMERIC,
    dose_unit TEXT,

    frequency_raw TEXT,
    frequency_interval_hours INTEGER CHECK (frequency_interval_hours > 0),
    frequency_times_per_day INTEGER CHECK (frequency_times_per_day > 0),

    duration_raw TEXT,
    duration_days INTEGER CHECK (duration_days >= 0),

    criteria_care_setting TEXT,
    criteria_allergy TEXT,
    criteria_pregnancy TEXT,
    criteria_renal_impairment TEXT,
    criteria_hepatic_impairment TEXT,
    criteria_other TEXT
);
COMMENT ON TABLE recommendations IS 'Detailed treatment recommendations linking diseases, evidence, and drugs.';
CREATE INDEX idx_recommendations_disease_id ON recommendations(disease_id);
CREATE INDEX idx_recommendations_evidence_id ON recommendations(evidence_id);
CREATE INDEX idx_recommendations_drug_id ON recommendations(drug_id);
CREATE INDEX idx_recommendations_population ON recommendations(population);
CREATE INDEX idx_recommendations_type ON recommendations(recommendation_type);

-- =================================================================
-- JUNCTION TABLES
-- =================================================================
CREATE TABLE disease_pathogens (
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    pathogen_id TEXT NOT NULL REFERENCES pathogens(pathogen_id) ON DELETE CASCADE,
    PRIMARY KEY (disease_id, pathogen_id)
);

CREATE TABLE recommendation_pathogens (
    recommendation_id TEXT NOT NULL REFERENCES recommendations(recommendation_id) ON DELETE CASCADE,
    pathogen_id TEXT NOT NULL REFERENCES pathogens(pathogen_id) ON DELETE CASCADE,
    PRIMARY KEY (recommendation_id, pathogen_id)
);

-- =================================================================
-- GENERIC TABLES (diagnostics, stewardship, monitoring, follow_up, referral)
-- =================================================================
CREATE TABLE diagnostics (
    diagnostic_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    page INTEGER
);
CREATE INDEX idx_diagnostics_disease_id ON diagnostics(disease_id);

CREATE TABLE stewardship (
    stewardship_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    page INTEGER
);
CREATE INDEX idx_stewardship_disease_id ON stewardship(disease_id);

CREATE TABLE monitoring (
    monitoring_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    page INTEGER
);
CREATE INDEX idx_monitoring_disease_id ON monitoring(disease_id);

CREATE TABLE follow_up (
    follow_up_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    page INTEGER
);
CREATE INDEX idx_follow_up_disease_id ON follow_up(disease_id);

CREATE TABLE referral (
    referral_id TEXT PRIMARY KEY,
    disease_id TEXT NOT NULL REFERENCES diseases(disease_id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    page INTEGER
);
CREATE INDEX idx_referral_disease_id ON referral(disease_id);

COMMIT;