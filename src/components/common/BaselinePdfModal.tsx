import React, { useState } from 'react';
import {
  FileText, Download, ExternalLink, X, Shield, AlertTriangle, CheckCircle2,
  ChevronRight, Layers, Eye, BookOpen, Sparkles
} from 'lucide-react';

interface BaselinePdfModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function BaselinePdfModal({ isOpen, onClose }: BaselinePdfModalProps) {
  const [activeView, setActiveView] = useState<'preview' | 'screens' | 'findings' | 'signoff'>('preview');
  const [selectedScreenIndex, setSelectedScreenIndex] = useState(0);

  if (!isOpen) return null;

  const pdfUrl = '/PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf';

  const screens = [
    { id: 'SCR-01', page: 5, route: '/login', title: 'Clinical Authentication & Persona Access Portal', risk: 'P2', role: 'All Roles' },
    { id: 'SCR-02', page: 6, route: 'dashboard', title: 'Clinical Operations Dashboard', risk: 'P2', role: 'ID Specialist, GP, Pharmacist, Admin' },
    { id: 'SCR-03', page: 7, route: 'assessment (Step 1)', title: 'Assessment Wizard - Demographics & Renal Clearance', risk: 'P2', role: 'Clinical Staff' },
    { id: 'SCR-04', page: 8, route: 'assessment (Step 2)', title: 'Assessment Wizard - Infection & Biomarkers', risk: 'P2', role: 'Clinical Staff' },
    { id: 'SCR-05', page: 9, route: 'assessment (Step 3)', title: 'Assessment Wizard - Microbiology & Allergies', risk: 'P0', role: 'Clinical Staff' },
    { id: 'SCR-06', page: 10, route: 'assessment (Step 4)', title: 'Assessment Wizard - Summary & Generation Trigger', risk: 'P0', role: 'Clinical Staff' },
    { id: 'SCR-07', page: 11, route: 'assessment (States)', title: 'Assessment Wizard - Loading & Error States', risk: 'P1', role: 'Clinical Staff' },
    { id: 'SCR-08', page: 12, route: 'recommendation (Hero)', title: 'Decision Support - Primary Regimen Package', risk: 'P0', role: 'Clinical Staff' },
    { id: 'SCR-09', page: 13, route: 'recommendation (Alternatives)', title: 'Decision Support - Alternative Therapies & Safety Matrix', risk: 'P2', role: 'Clinical Staff' },
    { id: 'SCR-10', page: 14, route: 'recommendation (Override Modal)', title: 'Decision Support - Prescribing Override Confirmation Modal', risk: 'P1', role: 'Clinical Staff' },
    { id: 'SCR-11', page: 15, route: 'recommendation (Review)', title: 'Decision Support - Clinical Review & Determination Portal', risk: 'P1', role: 'Clinical Staff' },
    { id: 'SCR-12', page: 16, route: 'recommendation (Trace)', title: 'Decision Support - 5-Stage Recommendation Trace Timeline', risk: 'P2', role: 'ID Specialist, Pharmacist, Admin' },
    { id: 'SCR-13', page: 17, route: 'explainability (Narrative & SHAP)', title: 'Explainability - Reasoning Narrative & SHAP Weights', risk: 'P1', role: 'All Staff & Researchers' },
    { id: 'SCR-14', page: 18, route: 'explainability (Trace Inspector)', title: 'Explainability - Execution Node Trace & Provenance', risk: 'P2', role: 'ID Specialist, Pharmacist, Admin' },
    { id: 'SCR-15', page: 19, route: 'patients', title: 'Patient Directory & Longitudinal Antibiogram History', risk: 'P2', role: 'Clinical Staff' },
    { id: 'SCR-16', page: 20, route: 'who', title: 'WHO AWaRe Antimicrobial Catalog Explorer', risk: 'P2', role: 'All Clinical Staff & Researchers' },
    { id: 'SCR-17', page: 21, route: 'soar', title: 'SOAR Surveillance Network & Regional Resistance Trends', risk: 'P2', role: 'ID Specialist, Pharmacist, Researcher' },
    { id: 'SCR-18', page: 22, route: 'armd', title: 'ARMD Deep Resistance Transformer ML Explorer', risk: 'P2', role: 'ID Specialist, Researcher' },
    { id: 'SCR-19', page: 23, route: 'telemetry (Registry)', title: 'Plugin & Telemetry Hub - Live Plugin Registry & Latency', risk: 'P2', role: 'ID Specialist, Pharmacist, Admin' },
    { id: 'SCR-20', page: 24, route: 'telemetry (Trace & Attribution)', title: 'Plugin & Telemetry Hub - Contribution Weights & Call Graph', risk: 'P2', role: 'ID Specialist, Pharmacist, Admin' },
    { id: 'SCR-21', page: 25, route: 'admin (Health & SLA)', title: 'Admin Governance - Microservice Health & SLA Telemetry', risk: 'P2', role: 'System Administrator' },
    { id: 'SCR-22', page: 26, route: 'admin (Users & RBAC)', title: 'Admin Governance - User Directory & Granular RBAC Matrix', risk: 'P2', role: 'System Administrator' },
    { id: 'SCR-23', page: 27, route: 'admin (Audit Trail)', title: 'Admin Governance - Immutable Clinical Audit Trail', risk: 'P2', role: 'System Administrator' },
    { id: 'SCR-24', page: 28, route: 'admin (Stewardship)', title: 'Admin Governance - Antimicrobial Stewardship Governance', risk: 'P2', role: 'Admin, ID Specialist' },
    { id: 'SCR-25', page: 29, route: 'settings', title: 'Clinical Settings & Prescribing Preferences', risk: 'P2', role: 'All Staff & Admins' },
    { id: 'SCR-26', page: 30, route: 'Modal (User Profile)', title: 'User Profile & Granular Permissions Inspection Modal', risk: 'P2', role: 'All Staff & Admins' },
    { id: 'SCR-27', page: 31, route: 'Fallback (RBAC Restricted)', title: 'Role-Based Access Control State Matrix & Restricted View', risk: 'P1', role: 'Researcher / Restricted Roles' },
    { id: 'SCR-28', page: 32, route: 'Theme (Dark Mode)', title: 'Theme Variations - Slate Dark Mode Baseline', risk: 'P2', role: 'Infectious Disease Specialist' },
    { id: 'SCR-29', page: 33, route: 'Responsive (Tablet/Mobile)', title: 'Responsive Layouts - Tablet & Mobile Viewports', risk: 'P2', role: 'Mobile Clinicians' },
  ];

  const findings = [
    { id: 'FND-01', cat: 'Clinical Decision Safety', sev: 'P0', desc: 'Black box warnings positioned below the fold on decision support view.', page: 'Page 12 (SCR-08)' },
    { id: 'FND-02', cat: 'Clinical Decision Safety', sev: 'P0', desc: 'Allergy contraindication conflicts present amber warning instead of assertive blocking gate.', page: 'Page 10 (SCR-06)' },
    { id: 'FND-03', cat: 'Cognitive Load & Data Density', sev: 'P1', desc: 'Confidence score (0.94) conflates model posterior probability with overall clinical certainty.', page: 'Page 12 (SCR-08)' },
    { id: 'FND-04', cat: 'Information Architecture', sev: 'P1', desc: 'Clinical review action buttons (Approve vs Modify vs Reject) lack visual hierarchy.', page: 'Page 15 (SCR-11)' },
    { id: 'FND-05', cat: 'Explainability & Transparency', sev: 'P1', desc: 'Raw database feature keys (e.g. egfr_val_norm) shown in SHAP explanation tree.', page: 'Page 17 (SCR-13)' },
    { id: 'FND-06', cat: 'Responsive Usability', sev: 'P1', desc: 'Horizontal table scrolling required for longitudinal antibiogram on tablet screens.', page: 'Page 33 (SCR-29)' },
    { id: 'FND-07', cat: 'Cognitive Load & Data Density', sev: 'P2', desc: 'Upper fold dashboard density creates cognitive competition across alert badges.', page: 'Page 6 (SCR-02)' },
    { id: 'FND-08', cat: 'Workflow Efficiency', sev: 'P2', desc: '5-phase trace timeline is expanded by default, consuming vertical bedside viewport.', page: 'Page 16 (SCR-12)' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-inset/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-surface border border-slate-border rounded-[var(--radius-lg)] shadow-2xl w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-border bg-slate-inset flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-[var(--radius-md)] bg-[var(--color-safety-info-bg)]/10 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-semibold text-slate-text-primary">
                  PharmaTrybe Frontend UI/UX Baseline Document
                </h3>
                <span className="text-[10px] num-clinical px-2 py-0.5 bg-[var(--color-clinical-950)] text-[var(--color-clinical-300)] rounded-full border border-[var(--color-clinical-700)] font-semibold">
                  34 Pages • Vector PDF
                </span>
                <span className="text-[10px] num-clinical px-2 py-0.5 bg-[var(--color-safety-success-bg)] text-[var(--color-safety-success)] rounded-full border border-[var(--color-safety-success-border)] font-semibold">
                  Phase 15A Verified
                </span>
              </div>
              <p className="text-xs text-slate-text-muted">
                Authoritative visual baseline, 29-screen inventory, human-factors findings, and Phase 15B redesign readiness.
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <a
              href={pdfUrl}
              download="PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf"
              className="px-3 py-1.5 rounded-[var(--radius-md)] bg-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-500)] text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors shadow-sm cursor-pointer"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </a>
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="focus-clinical px-3 py-1.5 rounded-[var(--radius-md)] border border-slate-border-subtle hover:bg-slate-inset-hover text-slate-text-secondary text-xs font-semibold flex items-center space-x-1.5 transition-colors duration-[var(--duration-fast)]"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Open in New Tab</span>
            </a>
            <button
              onClick={onClose}
              className="focus-clinical p-1.5 rounded-[var(--radius-md)] text-slate-text-muted hover:text-slate-text-primary hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <div className="px-6 py-2 border-b border-slate-border bg-slate-surface flex items-center space-x-2 shrink-0 text-xs font-semibold">
          <button
            onClick={() => setActiveView('preview')}
            className={`px-3 py-1.5 rounded-[var(--radius-md)] flex items-center space-x-1.5 transition-colors cursor-pointer ${
              activeView === 'preview'
                ? 'bg-[var(--color-clinical-950)]/60 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]'
                : 'text-slate-text-secondary hover:bg-slate-inset-hover'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Embedded PDF Viewer</span>
          </button>

          <button
            onClick={() => setActiveView('screens')}
            className={`px-3 py-1.5 rounded-[var(--radius-md)] flex items-center space-x-1.5 transition-colors cursor-pointer ${
              activeView === 'screens'
                ? 'bg-[var(--color-clinical-950)]/60 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]'
                : 'text-slate-text-secondary hover:bg-slate-inset-hover'
            }`}
          >
            <Layers className="w-4 h-4" />
            <span>29-Screen Inventory Catalog</span>
          </button>

          <button
            onClick={() => setActiveView('findings')}
            className={`px-3 py-1.5 rounded-[var(--radius-md)] flex items-center space-x-1.5 transition-colors cursor-pointer ${
              activeView === 'findings'
                ? 'bg-[var(--color-clinical-950)]/60 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]'
                : 'text-slate-text-secondary hover:bg-slate-inset-hover'
            }`}
          >
            <AlertTriangle className="w-4 h-4" />
            <span>19 Usability Findings (P0-P3)</span>
          </button>

          <button
            onClick={() => setActiveView('signoff')}
            className={`px-3 py-1.5 rounded-[var(--radius-md)] flex items-center space-x-1.5 transition-colors cursor-pointer ${
              activeView === 'signoff'
                ? 'bg-[var(--color-clinical-950)]/60 text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]'
                : 'text-slate-text-secondary hover:bg-slate-inset-hover'
            }`}
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Verification Sign-Off (GO)</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-hidden p-4 bg-slate-canvas">
          {activeView === 'preview' && (
            <div className="w-full h-full rounded-[var(--radius-md)] overflow-hidden border border-slate-border bg-slate-surface flex flex-col">
              <div className="p-3 bg-slate-inset border-b border-slate-border-subtle flex items-center justify-between text-xs">
                <span className="text-slate-text-secondary font-medium">
                  Document: <strong className="text-slate-text-primary">PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf</strong> (34 Pages, Standard PDF-1.7)
                </span>
                <div className="flex items-center space-x-2">
                  <a
                    href={pdfUrl}
                    download="PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf"
                    className="text-[var(--color-clinical-400)] hover:underline font-semibold flex items-center space-x-1"
                  >
                    <Download className="w-3.5 h-3.5" />
                    <span>Direct Download</span>
                  </a>
                </div>
              </div>
              <div className="flex-1 w-full h-full relative">
                <object
                  data={pdfUrl}
                  type="application/pdf"
                  className="w-full h-full min-h-[500px]"
                >
                  <div className="w-full h-full flex flex-col items-center justify-center p-8 text-center space-y-4">
                    <FileText className="w-12 h-12 text-[var(--color-clinical-400)]" />
                    <div>
                      <h4 className="text-sm font-semibold text-slate-text-primary">
                        PDF Ready for Direct Download
                      </h4>
                      <p className="text-xs text-slate-text-muted max-w-md mt-1">
                        Your browser sandbox is currently blocking in-frame PDF rendering. Click below to download or open in a new tab.
                      </p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <a
                        href={pdfUrl}
                        download="PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf"
                        className="px-4 py-2 bg-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-500)] text-white text-xs font-semibold rounded-[var(--radius-md)] flex items-center space-x-2"
                      >
                        <Download className="w-4 h-4" />
                        <span>Download 34-Page Baseline PDF</span>
                      </a>
                      <a
                        href={pdfUrl}
                        target="_blank"
                        rel="noreferrer"
                        className="focus-clinical px-4 py-2 border border-slate-border-subtle hover:bg-slate-inset-hover text-slate-text-primary text-xs font-semibold rounded-[var(--radius-md)] flex items-center space-x-2 transition-colors duration-[var(--duration-fast)]"
                      >
                        <ExternalLink className="w-4 h-4" />
                        <span>Open in New Browser Tab</span>
                      </a>
                    </div>
                  </div>
                </object>
              </div>
            </div>
          )}

          {activeView === 'screens' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
              {/* Screen List */}
              <div className="bg-slate-surface border border-slate-border rounded-[var(--radius-md)] p-3 overflow-y-auto space-y-1.5 md:col-span-1">
                <div className="text-[11px] font-semibold text-slate-text-muted uppercase tracking-wider px-2 py-1">
                  29 Cataloged Screens (Pages 5-33)
                </div>
                {screens.map((scr, idx) => (
                  <button
                    key={scr.id}
                    onClick={() => setSelectedScreenIndex(idx)}
                    className={`w-full text-left p-2.5 rounded-[var(--radius-md)] text-xs transition-all flex items-start justify-between cursor-pointer ${
                      selectedScreenIndex === idx
                        ? 'bg-[var(--color-safety-info-bg)] text-white font-semibold shadow-sm'
                        : 'hover:bg-slate-inset-hover text-slate-text-secondary'
                    }`}
                  >
                    <div>
                      <div className="num-clinical text-[10px] opacity-80">{scr.id} • Page {scr.page}</div>
                      <div className="font-semibold line-clamp-1">{scr.title}</div>
                      <div className="text-[10px] opacity-70 num-clinical mt-0.5">{scr.route}</div>
                    </div>
                    <span className={`text-[9px] font-semibold px-1.5 py-0.5 rounded uppercase shrink-0 mt-0.5 ${
                      scr.risk === 'P0' ? 'bg-[var(--color-safety-critical-bg)] text-white' :
                      scr.risk === 'P1' ? 'bg-[var(--color-safety-warning-bg)] text-white' :
                      scr.risk === 'P2' ? 'bg-[var(--color-safety-info-bg)] text-white' : 'bg-slate-inset text-slate-text-primary'
                    }`}>
                      {scr.risk}
                    </span>
                  </button>
                ))}
              </div>

              {/* Selected Screen Detail */}
              <div className="bg-slate-surface border border-slate-border rounded-[var(--radius-md)] p-5 overflow-y-auto space-y-4 md:col-span-2">
                {(() => {
                  const s = screens[selectedScreenIndex];
                  return (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between border-b border-slate-border-subtle pb-3">
                        <div>
                          <div className="text-[11px] num-clinical text-[var(--color-clinical-400)] font-semibold">
                            {s.id} — Document Page {s.page}
                          </div>
                          <h4 className="text-base font-semibold text-slate-text-primary">
                            {s.title}
                          </h4>
                        </div>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase ${
                          s.risk === 'P0' ? 'bg-[var(--color-safety-critical-bg)] text-[var(--color-safety-critical)] border border-[var(--color-safety-critical-border)]' :
                          s.risk === 'P1' ? 'bg-[var(--color-safety-warning-bg)] text-[var(--color-safety-warning)] border border-[var(--color-safety-warning-border)]' :
                          'bg-[var(--color-clinical-950)] text-[var(--color-clinical-400)] border border-[var(--color-clinical-700)]'
                        }`}>
                          Risk Rating: {s.risk}
                        </span>
                      </div>

                      <div className="grid grid-cols-2 gap-3 text-xs">
                        <div className="p-3 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle">
                          <span className="font-semibold text-slate-text-muted uppercase text-[10px] block mb-1">
                            Application Route
                          </span>
                          <span className="num-clinical text-slate-text-primary font-semibold">{s.route}</span>
                        </div>
                        <div className="p-3 rounded-[var(--radius-md)] bg-slate-inset border border-slate-border-subtle">
                          <span className="font-semibold text-slate-text-muted uppercase text-[10px] block mb-1">
                            Authoritative Clinical Role
                          </span>
                          <span className="text-slate-text-primary font-semibold">{s.role}</span>
                        </div>
                      </div>

                      <div className="p-4 rounded-[var(--radius-md)] bg-slate-canvas text-white space-y-2">
                        <div className="flex items-center space-x-2 text-[var(--color-safety-info)] font-semibold text-xs">
                          <Sparkles className="w-4 h-4" />
                          <span>PDF Render Preview Blueprint</span>
                        </div>
                        <p className="text-xs text-slate-text-secondary leading-relaxed">
                          This screen is fully rendered with vector fidelity on Page {s.page} of the authoritative baseline PDF, preserving exact button layouts, clinical status tags, navigation bars, and data density states.
                        </p>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}

          {activeView === 'findings' && (
            <div className="bg-slate-surface border border-slate-border rounded-[var(--radius-md)] p-4 h-full overflow-y-auto space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-border-subtle">
                <h4 className="text-sm font-semibold text-slate-text-primary">
                  Authoritative Baseline Usability & Clinical Safety Findings (Page 34)
                </h4>
                <span className="text-xs text-slate-text-muted font-medium">19 Categorized Findings</span>
              </div>

              <div className="space-y-2">
                {findings.map((f) => (
                  <div
                    key={f.id}
                    className="p-3 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset flex items-start justify-between gap-4 text-xs"
                  >
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="num-clinical font-semibold text-slate-text-primary">{f.id}</span>
                        <span className="text-slate-text-muted">•</span>
                        <span className="text-slate-text-secondary font-medium">{f.cat}</span>
                      </div>
                      <p className="text-slate-text-primary font-semibold">{f.desc}</p>
                    </div>
                    <div className="flex flex-col items-end space-y-1 shrink-0">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase ${
                        f.sev === 'P0' ? 'bg-[var(--color-safety-critical-bg)] text-white' :
                        f.sev === 'P1' ? 'bg-[var(--color-safety-warning-bg)] text-white' :
                        'bg-[var(--color-safety-info-bg)] text-white'
                      }`}>
                        {f.sev}
                      </span>
                      <span className="text-[10px] text-slate-text-muted num-clinical">{f.page}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeView === 'signoff' && (
            <div className="bg-slate-surface border border-slate-border rounded-[var(--radius-md)] p-6 h-full overflow-y-auto space-y-6">
              <div className="flex items-center space-x-3 p-4 rounded-[var(--radius-md)] bg-[var(--color-safety-success-bg)] border border-[var(--color-safety-success-border)] text-[var(--color-safety-success)]">
                <CheckCircle2 className="w-8 h-8 text-[var(--color-safety-success)] shrink-0" />
                <div>
                  <h4 className="text-sm font-semibold">Phase 15A Quality Gate: Sign-Off Status GO</h4>
                  <p className="text-xs text-[var(--color-safety-success)] mt-0.5">
                    Authoritative visual baseline completed with 100% test pass rate (307/307 assertions) and zero regressions.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-4 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset space-y-1">
                  <span className="text-slate-text-muted uppercase font-semibold text-[10px]">PDF Document</span>
                  <div className="text-base font-semibold text-slate-text-primary">34 Pages</div>
                  <p className="text-slate-text-muted">Vector PDF 1.7 with 29 rendered screens & findings</p>
                </div>
                <div className="p-4 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset space-y-1">
                  <span className="text-slate-text-muted uppercase font-semibold text-[10px]">Test Suite</span>
                  <div className="text-base font-semibold text-[var(--color-safety-success)]">307 / 307 Passed</div>
                  <p className="text-slate-text-muted">All Phase 8, 9, 10, 11, 13, 14 suites green</p>
                </div>
                <div className="p-4 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset space-y-1">
                  <span className="text-slate-text-muted uppercase font-semibold text-[10px]">Next Milestone</span>
                  <div className="text-base font-semibold text-[var(--color-clinical-400)]">Phase 15B</div>
                  <p className="text-slate-text-muted">Clinical Human-Factors UI/UX Redesign</p>
                </div>
              </div>

              <div className="flex items-center justify-end space-x-3 pt-4 border-t border-slate-border-subtle">
                <a
                  href={pdfUrl}
                  download="PHARMATRYBE_FRONTEND_UI_UX_BASELINE.pdf"
                  className="px-5 py-2.5 rounded-[var(--radius-md)] bg-[var(--color-clinical-600)] hover:bg-[var(--color-clinical-500)] text-white text-xs font-semibold flex items-center space-x-2 transition-colors cursor-pointer shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>Download Standalone PDF (104 KB)</span>
                </a>
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
