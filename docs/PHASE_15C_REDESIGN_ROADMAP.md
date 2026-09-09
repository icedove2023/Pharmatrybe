# PharmaTrybe CDSS — Phase 15C Redesign Roadmap & Tracking

**Status legend:** ✅ Done · 🔄 In progress · ⬜ Not started

Backend capability truth (locked, do not deviate):
- **Knowledge plugin (only one):** WHO AWaRe
- **Prediction / surveillance capabilities:** SOAR, ARMD (never labeled "knowledge")
- **Inbuilt platform components (never shown as registered plugins):** Clinical Rules, Decision Fusion, Explainability, Audit & Telemetry

---

## Phase A — Design Foundation
| Item | Status |
|---|---|
| Design tokens (`src/index.css`: clinical blue / smoke white / slate / safety semantics, radii, motion, type) | ✅ |
| `ui/SafetyAlert.tsx` (4-level alert: critical/warning/info/success) | ✅ |
| `ui/StatusBadge.tsx` | ✅ |
| `ui/Accordion.tsx` | ✅ |
| `ui/ClinicalButton.tsx` | ✅ |
| `ui/Drawer.tsx`, `ui/Modal.tsx`, `ui/Card.tsx`, `ui/EmptyState.tsx`, `ui/LoadingState.tsx`, `ui/DataTable.tsx` | ⬜ |

## Phase B — App Shell
| Item | Status |
|---|---|
| Login / auth portal | ⬜ |
| Header (streamlined, role/theme, notifications) | ✅ | Removed decorative "AWaRe Engine 2026" badge & trace-ID pill (unnecessary telemetry); retokenized |
| Sidebar (role-aware: Clinical / Knowledge & Surveillance / Administration / Account; WHO, SOAR, ARMD as separate items, no "Surveillance" mega-section) | ✅ | Regrouped exactly per spec §5; group renamed "Surveillance" → "Knowledge & surveillance" |
| Profile / session modal | ⬜ |

## Wave 1 — Highest Clinical Risk (P0/P1) — MOSTLY COMPLETE
| Component | Status | Notes |
|---|---|---|
| `PatientContextBanner` | ✅ | Retokenized, salient allergy alert, expandable details |
| `PrimaryRecommendationHero` | ✅ | Confidence vs. certainty separated; warnings adjacent, not below fold |
| `ClinicalWarningsPanel` | ✅ | 4-tier alert hierarchy via `SafetyAlert` |
| `ClinicalSafetyMatrix` | ✅ | Filter pills (All/Triggered/Passed), expandable rule detail, accessible tabs |
| `ClinicalReviewSection` (Approve/Modify/Reject) | ✅ | Clear hierarchy: Approve primary (filled), Modify secondary, Reject destructive-outline |
| `PrescribingOverrideModal` | ✅ | role="dialog", mandatory rationale, immutability notice via `SafetyAlert` |
| `AssessmentWizard` Step 4 (allergies/risk factors) | ✅ | NKDA quick-check, salient severe-allergy `SafetyAlert`, retokenized |
| `AssessmentWizard` Step 5 (review & generate) | ✅ | Pre-flight safety check surfaced above summary (was buried); disclaimer added |
| `AssessmentWizard` header/stepper/footer | ✅ | Retokenized; Steps 1–3 field bodies still on legacy styling (cosmetic only, functions unchanged) |
| `RecommendationView` (orchestrator) | ✅ | Reflowed: Authority banner → Safety gate → Patient → Hero → Rationale → Alternatives → Safety matrix → Determination → Evidence (accordion) → Technical trace (accordion) |
| `RecommendationTraceTimeline` | ✅ (structurally) | Now sits behind "Inspect pipeline trace" accordion; internal styling still legacy |

**Verification after Wave 1:** `tsc --noEmit` clean · all 307 test assertions passing.

**Known remaining polish in Wave 1 scope (deferred, non-blocking):** Steps 1–3 of `AssessmentWizard` (demographics/presentation/labs field styling) and the internals of `RecommendationTraceTimeline`, `AlternativeRecommendationsList`, `GuidelineReferencesPanel`, `StewardshipFindingsPanel`, `EvidenceRankingSection`, `EvidenceAttributionSection`, `AuditProvenanceBlock` still use pre-redesign light/dark Tailwind classes rather than tokens — functionally correct and already behind progressive disclosure, but visually inconsistent with the new palette. Will retokenize in a follow-up pass.

## Wave 2 — Dashboard, Patients, Explainability — ✅ COMPLETE
| Component | Status | Notes |
|---|---|---|
| `DashboardView` | ✅ | Removed gradient intro hero + always-visible plugin wall + on-dashboard Access/Watch/Reserve explainer (per §9, belongs in WHO explorer). "New case assessment" is now the primary action; plugin list replaced with compact "Registered integrations ▾" popover (WHO/SOAR/ARMD only, sourced from live `/api/v1/plugins`, not fabricated); skeleton loading states |
| `PatientHistoryView` | ✅ | Retokenized, animated timeline entrance (staggered), animated audit-payload modal (`AnimatePresence`), empty states for no patients / no history, skeleton loading |
| `ExplainabilityView` | ✅ | Restructured clinical-first: narrative → ranked evidence, with pipeline graph + SHAP attribution moved behind "Inspect model contribution" accordion and audit trail behind its own accordion (was always-visible engineering wall) |
| `ClinicalReasoningNarrative` | ✅ | Retokenized, reveal animation, reframed header as "Why this recommendation?" |
| `EvidenceRankingPanel` | ✅ | Retokenized via `StatusBadge` |
| `EvidenceAttributionPanel` (SHAP chart) | ✅ | Retokenized chart colors/tooltip; honest empty state preserved (no fabricated SHAP values) |
| `PipelineExecutionTrace` | ✅ | Retokenized wrapper, node buttons, trace-step fallback list |
| `ExplainabilityAuditReference` | ✅ | **Fixed honesty issue:** removed fabricated "Cryptographically Verified Execution" claim (no backing field in `AuditTrail` type) and fabricated placeholder version numbers (`v1.0.0`, `2026.1`, etc.) — now shows "Not reported by backend" when data is absent, per §32 (never invent model versions/status) |

**Animation pass (per this checkpoint's brief):** Added `motion/react`-based transitions — page/tab-change fade, `PrimaryRecommendationHero` reveal-on-mount, `SafetyAlert` entrance for critical/warning levels, `ClinicalButton` tap feedback, patient-timeline staggered entrance, animated modals (`PatientHistoryView` audit dialog). All respect `prefers-reduced-motion` via `useReducedMotion()`. Added `Skeleton`/`SkeletonCard` primitive replacing bare spinners in Dashboard, RecommendationView, ExplainabilityView, PatientHistoryView loading states.

**Verification after Wave 2:** `tsc --noEmit` clean · `npm run build` succeeds · all 307 test assertions passing.

## Wave 3 — Knowledge & Surveillance — ✅ COMPLETE
| Component | Status | Notes |
|---|---|---|
| Plugin-registry-driven architecture | ✅ | New `usePluginRegistry` hook (shared source of truth, reused by Sidebar/Dashboard/Explorers), `pluginNav.ts` (route/icon mapping with graceful fallback), generic `PluginExplorerView` for any registered plugin without a dedicated UI. Sidebar's "Knowledge & surveillance" section is now generated from the live plugin registry, not hardcoded. **Finding:** the backend mock registry actually reports 6 plugins, not 3 — `who_aware`, `soar`, `armd` plus three additional KNOWLEDGE-type entries (`nice_guidelines`, `idsa_guidelines`, `stewardship_policy`) with no prior UI. Per your instruction, all registered plugins now surface in the sidebar and route to the generic explorer if they lack a specialized one — flagging this since it's more knowledge plugins than the "WHO is the only one" baseline assumed |
| `KnowledgeBaseExplorer` (WHO) | ✅ | Retokenized, animated disease-card list (staggered reveal), animated detail-panel transitions on selection, skeleton loading; AWaRe Access/Watch/Reserve legend lives here (not dashboard) per §9 |
| `DiseaseSearch`, `DiseaseDetail` (+ 9 sub-panels: Guideline/Recommendation/Evidence/Pathogen/Stewardship/Monitoring/Diagnostic/FollowUp/Referral) | ✅ | Retokenized via batch script; animated tab transitions |
| `SOARExplorer` | ✅ | Retokenized (teal accent, distinct from clinical blue to visually separate "prediction" from "knowledge"), animated data reveal, honest empty/error states |
| `ResistanceSummary`, `ResistanceTrend`, `SurveillanceFilters` | ✅ | Animated stat-card stagger, animated stacked bar chart entrance, shared filter component reused by SOAR/ARMD |
| `ARMDExplorer` | ✅ | **Removed forbidden purple/indigo AI-gradient header** (§35 explicitly forbids this) — replaced with clinical-blue token treatment consistent with WHO/SOAR; animated metric cards and chart entrance |
| Dead code cleanup | ✅ | Removed orphaned `SurveillanceExplorer.tsx` — an unrouted, unused merged SOAR+ARMD tab-switcher that was exactly the "Surveillance mega-section" anti-pattern §38 says to avoid |

**Verification after Wave 3:** `tsc --noEmit` clean · `npm run build` succeeds · all 307 test assertions passing.

**Open item carried forward:** the app's light/dark theme toggle (Header sun/moon icon) is still wired up and functional at the CSS level (`.dark` class strategy confirmed in compiled output), but all Wave 1–3 redesign work was built against fixed dark-mode token values (`slate-canvas`, `slate-surface`, etc.), not light-mode equivalents. Toggling to light theme will now look broken/inconsistent for every redesigned component. Need your direction: (a) commit to dark-only and remove the now-nonfunctional toggle, or (b) build proper light-mode token values for everything completed so far. Flagging before Wave 4 rather than guessing.

## Prerequisite — Light/Dark Theme Architecture — ✅ COMPLETE
| Item | Status | Notes |
|---|---|---|
| Token indirection layer | ✅ | `src/index.css` restructured: every semantic token (`slate-canvas/surface/border/text-*`, `safety-*-bg/border`) now resolves through a `--pt-*` runtime CSS variable, defined once in `:root` (light) and once in `.dark`. Components reference the semantic Tailwind utility only — zero per-component theme logic |
| New `slate-inset` / `slate-inset-hover` tokens | ✅ | Replaces the ad-hoc `bg-slate-800/NN` pattern used ~340 times across Waves 1–3 for nested/secondary surfaces |
| Global batch retheme | ✅ | Regex-driven pass (`retheme.py`) converted raw `bg-slate-800/900`, `border-slate-700/600` etc. across 56 files to theme-aware semantic classes |
| Verification | ✅ | Confirmed `.dark` class-strategy (not media-query) via compiled CSS output; light mode now renders correctly across all Wave 1–3 work |

## Wave 4 — Administration & Identity — IN PROGRESS
| Component | Status | Notes |
|---|---|---|
| **Landing page** | ✅ | New `LandingPage.tsx` — hero, capability cards (WHO/SOAR/ARMD), "Register your hospital" / "Sign in" / "Explore with a demo account" |
| **Hospital registration (signup)** | ✅ | New `HospitalRegistrationForm.tsx` — creates org + first Admin account via `authApi.registerHospital()`, zod-validated (`hospitalRegistrationSchema`) |
| **Rebuilt login** | ✅ | `LoginForm.tsx` rebuilt — real email/password sign-in for admin + employee accounts, demo personas kept but visually separated and clearly labeled as non-production |
| **Shared identity directory** | ✅ | New `src/api/directory.ts` — single source of truth (localStorage-backed) for orgs/users/credentials, replacing the old split where `authApi.login()` pattern-matched email substrings and never consulted the admin user list. Newly admin-provisioned employees can now actually log in |
| **Removed fabricated auto-login** | ✅ | `authStore.initialize()` no longer silently logs in a default clinician persona when no session exists — unauthenticated visitors see the landing/sign-in flow |
| **Admin: promote/demote Admin** | ✅ | `UserDirectoryPanel.tsx` — grant/revoke Admin access with confirmation modal, last-active-admin protection (client-side; documented as a server-side requirement too) |
| **Admin: provision employees** | ✅ | Existing "Add employee" flow extended — generates a temp password, displayed once via a copyable `SafetyAlert` (explicitly flagged in-UI as a demo-only pattern, not a production credential-delivery method) |
| **`BACKEND_REQUIREMENTS.md`** | ✅ | New doc: full data model, endpoint list (register-hospital, login, admin user CRUD, role/status updates), validation rules, security notes (password hashing, session/JWT, last-admin protection, rate limiting), and an explicit list of what the demo does *not* do |
| `MicroserviceHealthPanel` | ✅ | Retokenized (batch + manual: indigo icon → clinical) |
| `UserDirectoryPanel` | ✅ | Full rewrite — tokens, `SafetyAlert`/`ClinicalButton`/`StatusBadge`, animated modals |
| `AuditLogPanel` | ✅ | Retokenized (batch) |
| `StewardshipGovernancePanel` | ✅ | Retokenized (batch) |
| `AdminGovernanceView` | ✅ | Header gradient (slate→blue) and tab bar retokenized to clinical-blue treatment |
| `TelemetryDashboard` | ✅ | **Removed forbidden indigo gradient header**; **fixed fabricated version fallbacks** (`v0.2.0`, `WHO-v2023.1`, `Rules-v1.0.0`, `Stewardship-v1.0.0`, `v1.0.4-prod`, `Fusion-Ranked-v1.0` → all now "Not reported by backend" when the field is genuinely absent) |
| `PluginRegistryPanel` | ✅ | **Structural fix**: previously listed Clinical Rules / Decision Fusion / Explainability / Audit & Telemetry as filterable categories in the *same* registry list as WHO/SOAR/ARMD — directly contradicting the plugin-vs-inbuilt-component truth constraint. Rewritten: "Registered plugins" (knowledge + prediction only) is now the primary view; the four inbuilt components moved to a separate "Platform architecture components" accordion, explicitly labeled "Inbuilt — not a registered plugin." New `getExternalRegisteredPlugins()` / `getInbuiltPlatformComponents()` helpers in `pluginRegistry.ts` enforce this split at the data layer, not just presentation |
| `PluginContributionPanel` | ✅ | Fixed same fabricated version fallbacks (`v0.2.0`, `Rules-v1.0.0`, `v1.0.4-prod`) |
| `AuditProvenanceBlock` (recommendation view) | ✅ | Fixed same pattern (`v0.1.0-stewardship-rules`, `v1.0.0`, `pt-stewardship-v1.0`, `deterministic-fusion-v1.0` → "Not reported by backend") |
| `RecommendationTracePanel` | ✅ | Retokenized (batch) |
| Dead code cleanup | ✅ | Removed orphaned `src/components/cases/ClinicalCaseExplorer.tsx` (unrouted, unused, had a forbidden slate→blue gradient) |

**Verification after this checkpoint:** `tsc --noEmit` clean · `npm run build` succeeds · all 307 test assertions passing.

### Wave 4 — now closed
- ✅ Visual QA pass on landing/register/login flow: tightened mobile padding (`p-8` → `p-5 sm:p-8` on auth cards, wrapper `p-4` → `p-3` on mobile) so the auth flow fits comfortably at the 390×844 target without cramping the demo-persona 3-column grid.
- ✅ `BACKEND_REQUIREMENTS.md` extended with plugin registry, audit export, and stewardship policy endpoints (§6), including an explicit note that `GET /api/v1/plugins` must never return Clinical Rules/Decision Fusion/Explainability/Audit — the frontend's client-side category filter should not be the only thing enforcing that boundary.
- ✅ `AdminDashboardView` confirmed as a thin wrapper — no work needed.

## Wave 1 deferred polish — now closed
| Item | Status | Notes |
|---|---|---|
| `AssessmentWizard` Steps 1–3 | ✅ | Fully retokenized (was previously only header/stepper/Step 4/5) — all `dark:` pairs replaced with semantic tokens |
| `RecommendationTraceTimeline` | ✅ | Retokenized, `sky-*` accent → clinical tokens |
| `AlternativeRecommendationsList` | ✅ | Retokenized |
| `GuidelineReferencesPanel` | ✅ | Retokenized |
| `StewardshipFindingsPanel` | ✅ | Retokenized |
| `EvidenceRankingSection` | ✅ | Retokenized, `indigo-*` accent → clinical tokens |
| `EvidenceAttributionSection` | ✅ | Retokenized |
| `AuditProvenanceBlock` | ✅ | Already fixed for fabricated fallbacks in Wave 4; now also fully retokenized |
| Dead code: `CandidateExtractionTrace.tsx`, `StewardshipMonitoringPanel.tsx` | ✅ | Confirmed orphaned (unrouted, no barrel export) and removed |

**Verification:** `tsc --noEmit` clean · `npm run build` succeeds · all 307 test assertions passing.

## Full UI/UX Consistency Audit — ✅ COMPLETE
Personal screen-by-screen audit requested before Wave 5: every remaining component using
pre-redesign paired `dark:` Tailwind classes was reviewed and migrated to the token system,
not just batch-replaced — each file was checked for genuine UX issues (modal animation
consistency, focus states, radius consistency, honest data) while retokenizing.

| Component | Status | Notes |
|---|---|---|
| `SettingsView` | ✅ | Full rewrite — theme picker as 3 real buttons (was a form control), toggle switch for AWaRe strict mode, save-toast feedback |
| `AuthGuard` | ✅ | Full rewrite — consistent with `SafetyAlert`/`ClinicalButton`, added `RefreshCw`-driven role-switch sandbox instead of static text |
| `RoleBadge` | ✅ | Rewritten to match `StatusBadge`'s radius convention (was `rounded-full` pill, now `rounded-[var(--radius-sm)]` for consistency across all badge components) |
| `UserSessionModal` | ✅ | Full rewrite — now uses `AnimatePresence`/motion like every other modal in the app (was a plain conditional div with no entrance/exit animation — inconsistent with Wave 1-3 modals); fixed a broken "Done" button (`bg-slate-canvas dark:bg-slate-100` — inverted, nonsensical) |
| `Breadcrumbs` | ✅ | Retokenized |
| `ProvenanceBadge` | ✅ | Radius aligned to `rounded-[var(--radius-xs)]` (was `rounded-full`, inconsistent with `StatusBadge`) |
| `BaselinePdfModal` | ✅ | Fully retokenized (403 lines, internal reference viewer) |
| `AuditLogPanel`, `MicroserviceHealthPanel`, `StewardshipGovernancePanel` | ✅ | Fully retokenized |
| `AdminGovernanceView` | ✅ | Fixed last remaining raw rose color pair |
| `PluginContributionPanel`, `RecommendationTracePanel`, `TelemetryDashboard` | ✅ | Fully retokenized |
| All 8 remaining WHO knowledge sub-panels (`EvidencePanel`, `FollowUpPanel`, `GuidelinePanel`, `MonitoringPanel`, `PathogenPanel`, `RecommendationPanel`, `ReferralPanel`, `StewardshipPanel`) | ✅ | Fully retokenized |

**Result:** `grep -rl "dark:" src/components` now returns only 3 files (`RoleBadge`, `UserSessionModal`
persona-switcher buttons, `ProvenanceBadge`) — all three are **intentional**, correctly-paired
role/provenance differentiator colors (purple/amber/teal/sky/cyan), not oversights. Every other
component in the entire `src/components` tree uses the token system exclusively.

**Also swept for:** forbidden purple/indigo gradients (none found beyond what was already fixed
in Wave 4), fabricated "Verified"/"Certified"/"Cryptographically" claims (none found beyond what
was already fixed).

**Verification:** `tsc --noEmit` clean · `npm run build` succeeds · all 307 test assertions passing.

## Wave 5 — Responsive, Settings, Error States, Final Audit
| Item | Status |
|---|---|
| `SettingsView` tabbed cleanup | ⬜ |
| Mobile/tablet responsive pass (390×844, 1024×768) | ⬜ |
| Empty / loading / error states across views | ⬜ |
| 404 / access-restricted fallback | ⬜ |
| Final visual QA + accessibility pass (WCAG 2.2 AA) | ⬜ |
| `tsc --noEmit` + `npm test` clean | ⬜ |

---

## Validation checkpoints (every wave)
1. `npx tsc --noEmit` clean
2. `npm test` (existing contract suites) still passing
3. No new/renamed API calls, no fabricated plugin/telemetry/status data
4. Visual consistency with tokens in `src/index.css`

## Explicitly out of scope
- Backend logic, API contracts, recommendation/ML algorithms
- Inventing capabilities not exposed by the current API clients (`src/api/*`)
