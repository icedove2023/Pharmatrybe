/**
 * Data Provenance Classification for Clinical & Administrative Values
 * 
 * Classifies data origin across the PharmaTrybe platform to prevent false authority
 * and ensure full transparency aligned with GMLP and medical software transparency principles.
 */
export type DataProvenance =
  | 'backend_authoritative' // Directly from verified backend endpoints / authoritative databases
  | 'client_observed'       // Measured or observed in the browser client (e.g. fetch response timing)
  | 'static_configuration'  // Known baseline target, system constant, or guideline definition
  | 'demo_fixture'          // Mock/demo baseline fixture (e.g. for offline demonstration or local preview)
  | 'unavailable';          // Field/metric not exposed or returned by backend

export interface ProvenanceMetadata {
  provenance: DataProvenance;
  sourceDescription?: string;
  isAuthoritative: boolean;
}
