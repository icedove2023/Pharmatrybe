# PharmaTrybe UI/UX Design Specification

**File:** `design.md`  
**Status:** Design baseline for frontend redesign  
**Scope:** Responsive clinical UI/UX aligned with the existing PharmaTrybe backend, frontend identity/RBAC integration, and approved architecture.

## 1. Purpose

PharmaTrybe is an Explainable AI Clinical Decision Support System for antimicrobial prescribing and stewardship. The frontend is a clinical work tool, not a consumer health application and not an autonomous prescribing interface.

The redesign must make existing backend capabilities usable and clinically meaningful without inventing functionality, permissions, clinical logic, or backend states.

Core experience:

```text
Clinical Context
      ↓
Safety Constraints
      ↓
Guideline / Knowledge Evidence
      ↓
Prediction Evidence
      ↓
Decision Fusion
      ↓
Recommendation
      ↓
Explanation
      ↓
Clinician Review / Decision
```

## 2. Authoritative Architecture

Implementation must remain aligned with:

- `docs/PROJECT_CONTEXT.md`
- `docs/architecture/Platform_Architecture_Baseline_v1.0.md`
- `docs/architecture/Data_Flow_and_Orchestration.md`
- `docs/architecture/Plugin_Framework.md`
- `docs/architecture/Plugin_Developer_Guide.md`
- `docs/architecture/Plugin_SDK_Architecture.md`
- `docs/integration/R10D_1_Frontend_Authentication_Boundary.md`
- `docs/integration/R10D_2_Frontend_Execution.md`
- `docs/integration/R10D_3_Frontend_Tenant.md`
- `docs/integration/R10D_4_Frontend_RBAC.md`
- `docs/integration/R10D_5_Protected_API_Integration.md`
- `docs/integration/R10D_6_Frontend_Identity_Security_Tests.md`
- `docs/integration/R10D_7_Frontend_Identity_RBAC_Integration_Inspection.md`

Non-negotiable principles:

1. Evidence precedes AI.
2. Clinicians retain final authority.
3. Every recommendation is explainable.
4. Prediction and knowledge remain separate.
5. Decision Fusion is deterministic.
6. Every antibiotic candidate traces to prediction evidence.
7. The platform is auditable.
8. Plugins contribute capabilities/evidence; they do not become clinical authority.
9. Frontend authorization is UX only; backend authorization remains authoritative.
10. Frontend communicates through FastAPI rather than directly to internal services/plugins.

## 3. Design Direction

### Clinical-first

Show what the clinician needs:

- patient context;
- clinical problem;
- important safety constraints;
- evidence;
- recommendation;
- alternatives;
- stewardship considerations;
- explanation;
- review state.

Do not make clinicians interpret:

- raw JSON;
- internal service names;
- class names;
- request IDs;
- plugin execution payloads;
- low-level telemetry;
- database IDs unless needed for audit/support.

### Explainability-first

Every recommendation must have a visible path to:

- rationale;
- guideline evidence;
- patient-specific safety findings;
- prediction evidence;
- stewardship evidence;
- alternatives;
- decision pathway.

Technical traces belong behind progressive disclosure.

### Calm clinical workspace

The visual goal is:

> clear, trustworthy, fast to scan, low cognitive load, safety-first.

Healthcare CDS usability should fit clinical workflow and reduce information overload; poor organization can increase mental workload and impair decision-making. citeturn0search0turn0search12

## 4. Global Application Shell

### Desktop

```text
┌──────────────────────────────────────────────────────────────┐
│ PharmaTrybe | Hospital | Search | Alerts | User             │
├───────────────┬──────────────────────────────────────────────┤
│ Dashboard     │ Page title + context                          │
│ New Assessment│                                                │
│ Cases         │ Main clinical/admin content                   │
│ Recommendations                                              │
│ Patients      │                                                │
│ AMR           │                                                │
│ Knowledge     │                                                │
│ Guidelines    │                                                │
│               │                                                │
│ Admin items   │                                                │
│ when allowed  │                                                │
└───────────────┴──────────────────────────────────────────────┘
```

### Mobile

- compact top bar;
- hospital context;
- single-column content;
- bottom navigation for frequent clinical tasks;
- slide-out menu for secondary/admin functions.

Primary mobile navigation:

`Home | New Case | Cases | Recommendations | More`

## 5. Brand and Design Tokens

The existing landing/login palette is the baseline brand palette. Refine it; do not replace it.

Use semantic tokens:

```css
--pt-primary
--pt-primary-hover
--pt-primary-soft
--pt-background
--pt-surface
--pt-surface-raised
--pt-border
--pt-text
--pt-text-secondary
--pt-text-muted
--pt-success
--pt-success-soft
--pt-warning
--pt-warning-soft
--pt-danger
--pt-danger-soft
--pt-info
--pt-info-soft
```

Actual values must be extracted from the existing `src/index.css` during implementation.

Status must never depend on color alone. Use text + icon + color.

### Typography

```text
Page title       28–32px
Section heading  20–24px
Card heading     16–18px
Body             14–16px
Metadata         12–13px
```

### Spacing

Use an 8px rhythm:

`4 / 8 / 12 / 16 / 24 / 32 / 48px`

## 6. Information Architecture

### Clinician / Pharmacist

```text
Dashboard
├── New Clinical Assessment
├── Clinical Cases
│   └── Case Detail
│       ├── Clinical Context
│       ├── Recommendation
│       └── Explanation
├── Recommendations
├── Patients
├── AMR Intelligence
│   ├── Surveillance
│   └── Resistance Prediction
├── Knowledge Base
└── Guidelines
```

### Hospital Administrator

```text
Dashboard
├── Professionals
├── Plugin Governance
│   ├── Registry
│   ├── Details
│   ├── Validation
│   ├── Approval
│   ├── Activation
│   └── Audit
├── Clinical Workflows
├── Audit Trail
├── System Health
└── Settings
```

Visibility is capability-driven from backend permission codes.

## 7. Screen Specifications

### 7.1 Landing

**User:** unauthenticated visitor.

Show:

- PharmaTrybe identity;
- concise CDSS purpose;
- evidence-based positioning;
- explainability;
- stewardship;
- secure hospital positioning;
- sign-in/onboarding.

Never show internal architecture, plugin telemetry, model traces, or raw backend information.

### 7.2 Login / Registration

Show:

- email;
- password;
- loading;
- validation;
- session-expired state;
- inactive-account state;
- forbidden/incomplete-identity state.

`401` means authentication/session problem.  
`403` means authenticated but not authorized.

### 7.3 Dashboard

**Primary users:** clinician/pharmacist.

The dashboard answers:

> What needs my attention now?

Priority content:

1. New Clinical Assessment.
2. Cases requiring attention.
3. Recommendations requiring review.
4. Important stewardship/safety alerts.
5. Recent clinical activity.
6. AMR summary.
7. Relevant knowledge/guideline updates.

Do not use it as a telemetry wall. No raw plugin logs, CPU/memory data, request IDs, model payloads, or internal service traces.

### 7.4 New Clinical Assessment

Use a guided workflow:

```text
1 Patient & Context
2 Clinical Details
3 Microbiology
4 Review
5 Decision Support
```

Show only clinically relevant input:

- patient identifier;
- age/sex when relevant;
- weight where relevant;
- allergies;
- clinical problem;
- severity;
- symptoms;
- relevant comorbidities;
- renal/pregnancy information when applicable;
- microbiology;
- susceptibility information;
- relevant laboratory findings.

Do not ask for technical fields that the backend can derive.

### 7.5 Clinical Cases

Show:

- case/patient identifier;
- clinical problem;
- date/time;
- case status;
- recommendation state;
- review state;
- warnings.

Provide filters for status, date, clinical problem, patient, and recommendation state.

Avoid unnecessary UUIDs and raw database fields.

### 7.6 Case Detail

Tabs:

```text
Overview | Clinical Context | Recommendation | Explanation | History
```

The default view summarizes the case instead of dumping every backend field.

### 7.7 Recommendation

The recommendation page answers:

> What is being suggested, why, what safety issues matter, and what alternatives exist?

Layout:

```text
Clinical Recommendation
Patient context

Recommended option
- antimicrobial
- route/dose/frequency/duration only if supplied by backend
- evidence/confidence context
- review status

Why this option?
Safety considerations
Alternatives
[View full explanation]
```

Never make prediction confidence appear to be a prescription or standalone truth.

Preferred wording:

- `CDSS recommendation`
- `Suggested option for clinician review`
- `Evidence-supported recommendation`

Avoid autonomous language such as `Auto-treat` or `Prescribe now` unless explicitly supported by a future clinical workflow.

### 7.8 Explainability

Visual pathway:

```text
Clinical Context
      ↓
Safety Rules
      ↓
Guideline Evidence
      ↓
Prediction Evidence
      ↓
Decision Fusion
      ↓
Recommendation
```

Evidence sections:

- guideline/source/version;
- relevant evidence;
- safety rule findings;
- prediction contribution;
- stewardship considerations;
- alternatives.

Technical trace is secondary and may expose version/trace/provenance information for authorized users.

### 7.9 Knowledge Base

Show:

- search;
- categories;
- disease/topic;
- drug;
- guideline source;
- evidence level;
- version;
- concise clinical content.

Do not expose plugin class names, database connections, or raw provider payloads.

### 7.10 Guidelines

Use:

`Guideline list → Guideline detail`

Show:

- source;
- version;
- topic;
- recommendation;
- evidence level;
- antimicrobial;
- contraindications;
- stewardship guidance.

### 7.11 AMR Surveillance

Show clinically meaningful:

- resistance trends;
- organism trends;
- susceptibility patterns;
- time range;
- hospital/unit context where authorized;
- important changes;
- data freshness.

Prefer simple trend charts and ranked bars. Avoid decorative analytics.

### 7.12 Resistance Prediction / ARMD

Show:

- predicted resistance/susceptibility;
- confidence/evidence strength;
- relevant contributing context;
- evidence;
- limitations;
- connection to the clinical recommendation.

Never imply:

`ARMD → treatment decision`

The conceptual flow is:

`ARMD evidence → Clinical Decision Engine → Recommendation`

### 7.13 Patient History

Show only information needed for antimicrobial decision support:

- patient identity appropriate to role;
- prior cases;
- prior recommendations;
- antimicrobial exposure;
- microbiology;
- resistance history;
- important allergies/safety information.

Do not turn this into an unrestricted EHR replacement.

### 7.14 Recommendations

Show:

- patient;
- clinical problem;
- recommendation;
- status;
- review state;
- date;
- important warning.

Filters:

- pending review;
- reviewed;
- requires attention;
- date;
- clinical problem.

### 7.15 Plugin Management

**Admin only.**

The plugin interface is governance, not clinical dashboarding.

List:

```text
Plugin | Category | Version | Status | Validation | Health | Owner | Updated | Actions
```

Categories should follow the architecture:

- Prediction;
- Knowledge;
- Risk;
- Rules;
- Reporting;
- Integration;
- Explainability where implemented.

Do not invent lifecycle states that the backend does not yet support.

### 7.16 Plugin Details

Show:

- human-readable name;
- category;
- version;
- owner/provider;
- capabilities;
- deployment type;
- compatibility;
- validation;
- health;
- lifecycle state;
- audit history;
- configuration status.

Technical metadata is progressive disclosure.

### 7.17 Plugin Upload / Registration

This is a governance workflow and must not be shown as operational until the backend lifecycle exists.

Future UX:

```text
Upload
 ↓
Inspect
 ↓
Manifest
 ↓
Validate
 ↓
Register
 ↓
Pending approval
 ↓
Approve
 ↓
Activate
```

The browser must never authoritatively set:

- artifact hash;
- hospital ownership;
- authorization;
- activation authority.

The backend owns those decisions.

### 7.18 Audit Trail

Show:

- timestamp;
- actor;
- action;
- resource;
- outcome;
- tenant/hospital context where appropriate;
- request/trace identifier;
- bounded provenance/version metadata.

Clinical provenance may include recommendation ID, model/plugin/knowledge/explanation versions, and trace ID.

Do not turn audit into a patient-data dumping ground.

### 7.19 System Health

Admin/support surface.

Show:

```text
Platform
Knowledge
Decision Engine
Prediction services
Plugin runtime
Storage
API
```

with:

`Healthy | Degraded | Unavailable`

Do not expose CPU, memory, process IDs, stack traces, containers, or raw logs on clinician screens.

### 7.20 Settings

Settings contains configuration, not unrelated operational screens.

User settings:

- profile;
- display;
- notifications;
- accessibility;
- session/security.

Hospital settings for authorized admins:

- hospital configuration;
- stewardship policy configuration where supported;
- workflow configuration where supported;
- approved plugin configuration;
- professional management where supported.

Do not put cases, recommendations, AMR analytics, plugin health, or audit history in Settings.

## 8. Role Experiences

### Clinician

```text
Dashboard
New Assessment
Cases
Recommendations
Patients
AMR Intelligence
Knowledge
Guidelines
```

### Pharmacist

Similar clinical experience with stewardship-oriented information where permitted.

### Hospital Administrator

```text
Dashboard
Professionals
Plugin Governance
Workflows
Audit
System Health
Settings
```

Do not create a new frontend role model. Use `/auth/me` roles and canonical permission codes.

## 9. Alerts and Safety

Alerts must be sparse and actionable.

Priority:

```text
Critical safety issue
↓
High-priority clinical concern
↓
Action required
↓
Informational
```

Each alert should answer:

1. What is wrong?
2. Why does it matter?
3. What should be reviewed?

Example:

```text
Allergy concern

Penicillin allergy is recorded for this patient.

This may affect suitability of the selected antimicrobial.

[Review safety evidence]
```

## 10. Loading / Empty / Error States

### Loading

Use skeletons and meaningful workflow state:

```text
Preparing clinical context...
Retrieving evidence...
Evaluating safety rules...
Generating explanation...
```

Never show fake percentages.

### Empty

Use actionable language:

> No clinical assessments yet. Start a new assessment to generate evidence-supported decision support.

### 401

> Your session has expired. Please sign in again.

### 403

> You do not have permission to access this area.

A `403` must not automatically become login.

### Clinical pipeline failure

> Decision support is currently unavailable. No recommendation was produced because the required evidence/explanation could not be completed. Please use established clinical guidance and clinical judgment.

This reflects the backend fail-safe rule: if required knowledge, decision fusion, or explainability cannot complete, a misleading recommendation must not be shown.

## 11. Responsive Rules

### Desktop ≥1200px

- persistent sidebar;
- multi-column cards;
- split evidence/detail views;
- readable tables;
- charts.

### Tablet 768–1199px

- collapsible sidebar;
- two-column layouts where useful;
- simplified tables;
- stacked evidence cards.

### Mobile <768px

- single-column;
- bottom navigation;
- large touch targets;
- cards instead of wide tables;
- full-screen detail views;
- sticky primary action where clinically appropriate.

Clinical assessment must be a real mobile workflow, not a desktop form squeezed onto a phone.

## 12. Accessibility

Require:

- keyboard navigation;
- visible focus;
- semantic HTML;
- screen-reader labels;
- adequate contrast;
- non-color status indicators;
- accessible validation/errors;
- adequate touch targets.

Critical safety information must remain understandable without color.

## 13. Technical Boundaries

The frontend renders backend-owned information.

| Data | Authority |
|---|---|
| Authenticated user | Supabase/backend |
| Hospital context | Backend |
| Roles | Backend |
| Permission codes | Backend |
| Recommendation | Decision Fusion/backend |
| Safety findings | Clinical Rules Engine |
| Guideline evidence | Knowledge layer |
| Prediction evidence | Prediction plugins |
| Explanation | Explainability Engine |
| Audit | Backend |
| Plugin health | Plugin Manager/backend |

Never move clinical reasoning into React/TypeScript.

Do not implement in frontend:

- antibiotic candidate generation;
- contraindication logic;
- clinical rules;
- decision fusion;
- recommendation ranking;
- explanation generation.

## 14. API Boundary

```text
Frontend
   ↓
Supabase access token
   ↓
FastAPI
   ↓
Clinical / Governance Services
   ↓
Supabase / Plugins
```

Do not introduce frontend-to-plugin communication.

## 15. Hardcoding Prohibitions

Do not hardcode:

- role permissions;
- hospital identity;
- clinical recommendations;
- antibiotic candidates;
- safety rules;
- model decisions;
- plugin authority;
- audit events;
- tenant ownership.

Presentation labels are acceptable; authoritative values must come from backend contracts.

## 16. Reusable Component Library

Core components:

```text
AppShell
Sidebar
TopBar
MobileNav
PageHeader
SectionHeader
Card
MetricCard
StatusBadge
SeverityBadge
AlertCard
PatientSummary
ClinicalContextCard
SafetySummary
RecommendationCard
AlternativeCard
EvidenceCard
GuidelineCard
PredictionEvidenceCard
DecisionTrace
ExplanationPanel
CaseList
CaseRow
RecommendationList
SearchBar
FilterBar
Stepper
FormSection
FormField
ValidationMessage
DataTable
EmptyState
LoadingSkeleton
ErrorState
ForbiddenState
PluginCard
PluginStatus
PluginValidationPanel
PluginAuditTimeline
AuditTimeline
SystemHealthCard
Modal
Drawer
ConfirmDialog
Toast
```

## 17. Implementation Rules for Copilot

Before editing UI code, Copilot must:

1. Read this document.
2. Read `docs/PROJECT_CONTEXT.md`.
3. Read the platform architecture.
4. Read all R10D integration documents.
5. Inspect existing frontend components.
6. Reuse the existing API client.
7. Reuse the existing Zustand auth/session store.
8. Reuse backend-derived permission codes.
9. Inspect existing `SafetyAlert` and `StatusBadge`.
10. Extract the actual landing/login palette from `src/index.css`.

Copilot must not create:

- a second auth store;
- a second API client;
- a second RBAC model;
- client-side clinical reasoning;
- fake endpoints;
- fake clinical data;
- fake plugin governance;
- invented permissions;
- invented backend lifecycle states.

## 18. Implementation Order

### UI-1 Design foundation

- design tokens;
- typography;
- spacing;
- buttons;
- cards;
- badges;
- alerts;
- shell;
- responsive foundation.

### UI-2 Clinical workflow

- Dashboard;
- New Assessment;
- Cases;
- Recommendation;
- Explainability.

### UI-3 Clinical intelligence

- Knowledge;
- Guidelines;
- AMR Surveillance;
- Resistance Prediction;
- Patient History.

### UI-4 Administration

- Plugin Management;
- Plugin Details;
- Audit;
- System Health;
- Settings.

### UI-5 Responsive/accessibility

- mobile;
- tablet;
- accessibility;
- loading;
- empty;
- error states.

### UI-6 Contract validation

Every screen must be checked against actual backend endpoints before being declared complete.

## 19. Backend-Ready vs Future UI

### Backend-backed now

Based on the current 10C/10D integration:

- Supabase authentication;
- session restoration;
- `/auth/me`;
- backend-derived hospital identity;
- roles;
- canonical permission codes;
- protected API requests;
- `401`/`403` behavior;
- existing clinical/backend surfaces that have actual API contracts.

### Future / conditional

The design may reserve UI space for:

- external plugin upload;
- full plugin approval lifecycle;
- production container isolation;
- expanded observability;
- end-to-end deployment testing;
- final clinical integration.

The UI must never pretend a future backend feature is operational.

## 20. Definition of Done

A screen is complete only when:

- primary user is defined;
- primary task is clear;
- backend capability is real;
- unnecessary internal data is hidden;
- RBAC is respected;
- desktop/mobile layouts work;
- loading/error/empty states exist;
- safety states are explicit;
- critical information is not color-only;
- clinical logic remains backend-owned;
- existing authenticated API boundary is used;
- lint/type/build checks pass.

## 21. Clinical Safety Acceptance Criteria

Before accepting a clinical-facing screen:

1. Patient/case context is immediately identifiable.
2. Recommendation cannot appear without an explanation path.
3. Safety warnings are prominent.
4. Alternatives are distinguishable from the primary recommendation.
5. Prediction evidence is not presented as a prescription.
6. Clinician review remains explicit.
7. Technical information is progressively disclosed.
8. Unauthorized data is not displayed.
9. Unauthorized actions are not exposed.
10. Failed explanation does not result in a misleading recommendation.

## 22. Final Experience

The product should communicate:

```text
WHO IS THIS PATIENT?
        ↓
WHAT IS THE CLINICAL PROBLEM?
        ↓
WHAT SAFETY ISSUES MATTER?
        ↓
WHAT EVIDENCE IS AVAILABLE?
        ↓
WHAT DOES THE CDSS SUGGEST?
        ↓
WHY?
        ↓
WHAT ALTERNATIVES EXIST?
        ↓
CLINICIAN DECIDES
```

The redesign is successful when PharmaTrybe feels like a calm, trustworthy clinical workspace rather than a software-engineering console.

---

**End of `design.md`**
