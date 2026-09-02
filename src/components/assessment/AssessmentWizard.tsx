import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  User, Activity, TestTube, ShieldAlert, CheckCircle2, ChevronRight, ChevronLeft,
  Plus, Sparkles, RefreshCw, Cpu, BookOpen, Layers, AlertCircle, AlertTriangle, Shield, Check, Info, FileText,
  ChevronDown, ChevronUp, AlertOctagon
} from 'lucide-react';
import { useClinicalCaseStore } from '@/stores/clinicalCaseStore';
import { recommendationApi } from '@/api';
import { ExecutionMode, ClinicalCase } from '@/types';
import { useAuthStore } from '@/stores/authStore';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { cn } from '@/lib/utils';
import { getExternalRegisteredPlugins } from '@/plugins/registry/pluginRegistry';
import { PluginGeneratedForm } from './PluginGeneratedForm';
import { useNotificationStore } from '@/stores/notificationStore';

interface AssessmentWizardProps {
  onCaseSubmitted: (caseId: string) => void;
}

export function AssessmentWizard({ onCaseSubmitted }: AssessmentWizardProps) {
  const {
    caseData,
    currentStep,
    setCurrentStep,
    updateDemographics,
    updatePresentation,
    updateLaboratory,
    updateRiskFactors,
    setExecutionMode,
    togglePluginSelection,
    loadPresetCase,
    resetCase,
  } = useClinicalCaseStore();

  const user = useAuthStore((state) => state.user);
  const hasPermission = useAuthStore((state) => state.hasPermission);
  const canSubmit = hasPermission('canSubmitAssessment');

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [showOptionalVitals, setShowOptionalVitals] = useState(false);
  const [showOptionalBiomarkers, setShowOptionalBiomarkers] = useState(false);
  const [showOptionalDetails, setShowOptionalDetails] = useState(false);

  const registeredPlugins = getExternalRegisteredPlugins();
  const activePlugins = (caseData.executionMode === 'AUTO'
    ? registeredPlugins
    : registeredPlugins.filter((plugin) => (caseData.pluginSelections || []).includes(plugin.backendId || plugin.id)));
  const hasPluginMix = activePlugins.some((plugin) => plugin.category === 'knowledge') && activePlugins.some((plugin) => plugin.category === 'prediction');

  const updatePluginField = (path: string, value: unknown) => {
    const [section, field] = path.split('.');
    if (!section || !field) return;
    const update = { [field]: value };
    if (section === 'demographics') updateDemographics(update);
    if (section === 'presentation') updatePresentation(update);
    if (section === 'laboratory') updateLaboratory(update);
    if (section === 'riskFactors') updateRiskFactors(update);
  };

  // TanStack Query Mutation for submitting clinical case
  const submitCaseMutation = useMutation({
    mutationFn: async (casePayload: ClinicalCase) => {
      return await recommendationApi.submitCase(casePayload);
    },
    onSuccess: (data) => {
      onCaseSubmitted(data.caseId);
    },
  });

  const steps = [
    { id: 1, label: 'Demographics & Setting', icon: User },
    { id: 2, label: 'Plugin-Generated Inputs', icon: Activity },
    { id: 3, label: 'Review & Run Pipeline', icon: CheckCircle2 },
  ];

  const validateStep = (stepNumber: number): boolean => {
    const errors: Record<string, string> = {};

    if (stepNumber === 1) {
      if (!caseData.demographics.age || caseData.demographics.age <= 0 || caseData.demographics.age > 125) {
        errors.age = 'Patient age must be between 1 and 125 years.';
      }
      if (!hasPluginMix) {
        errors.plugins = 'Select at least one knowledge plugin and one prediction plugin.';
      }
    }

    if (stepNumber === 2) {
      if (!caseData.presentation.primaryDiagnosis) {
        errors.primaryDiagnosis = 'Primary diagnosis / syndrome is required.';
      }
    }

    if (stepNumber === 3) {
      if (caseData.laboratory.egfr !== undefined && (caseData.laboratory.egfr < 0 || caseData.laboratory.egfr > 200)) {
        errors.egfr = 'eGFR must be between 0 and 200 mL/min/1.73m².';
      }
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep(currentStep)) return;
    if (currentStep === 2) setCurrentStep(3);
    else if (currentStep < 3) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    setFieldErrors({});
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const handleSubmit = () => {
    if (!validateStep(currentStep)) return;
    submitCaseMutation.mutate(caseData);
  };

  const availableSymptoms = [
    'High Fever (>38.5°C)',
    'Productive Cough',
    'Dyspnea / Shortness of Breath',
    'Pleuritic Chest Pain',
    'Dysuria / Burning Sensation',
    'Urinary Frequency',
    'Suprapubic Pain',
    'Erythema & Warmth on Skin',
    'Purulent Drainage',
    'Nausea / Vomiting',
    'Altered Mental Status / Confusion',
  ];

  const availableDiagnosis = [
    'Community-Acquired Pneumonia (CAP)',
    'Uncomplicated Acute Cystitis (UTI)',
    'Complicated Pyelonephritis',
    'Non-purulent Cellulitis (SSTI)',
    'Purulent Skin & Soft Tissue Infection',
    'Acute Bacterial Rhinosinusitis',
  ];

  const availableAllergies = [
    'Penicillin (Mild Rash reported 10 yrs ago)',
    'Penicillin (Anaphylaxis / Severe)',
    'Sulfa Drugs (Hives / Rash)',
    'Fluoroquinolones (Tendonitis / QTc Prolongation)',
    'Macrolides (GI Upset)',
    'Cephalosporins (Mild Rash)',
  ];

  const executionModes: { id: ExecutionMode; label: string; desc: string; icon: any }[] = [
    { id: 'AUTO', label: 'Automatic (Not Recommended)', desc: 'Use all available knowledge and prediction plugins and merge every exposed schema.', icon: Sparkles },
    { id: 'USER_SELECTED', label: 'Custom Plugins', desc: 'Choose any available plugins, with at least one knowledge and one prediction plugin required.', icon: ShieldAlert },
  ];

  // Has severe penicillin allergy
  const hasSeverePenicillin = caseData.riskFactors.allergies.some(a => a.toLowerCase().includes('anaphylaxis'));

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6 md:flex-row md:items-center">
        <div>
          <div className="mb-1 inline-flex items-center space-x-1.5 rounded-full bg-[var(--color-clinical-950)] px-2.5 py-0.5 text-xs font-semibold text-[var(--color-clinical-300)]">
            <Plus className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Clinical intelligence pipeline orchestration</span>
          </div>
          <h2 className="text-lg font-semibold text-slate-text-primary">Patient case & prescribing assessment</h2>
          <p className="text-xs text-slate-text-muted">
            Enter clinical parameters to initiate multi-source evidence fusion. Candidates originate strictly from
            prediction models and are filtered by deterministic safety rules.
          </p>
        </div>

      </div>

      {/* Stepper Navigation */}
      <div className="overflow-x-auto rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-4">
        <div className="flex min-w-[600px] items-center justify-between px-4">
          {steps.map((step) => {
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <React.Fragment key={step.id}>
                <button
                  type="button"
                  onClick={() => {
                    if (step.id <= currentStep || validateStep(currentStep)) setCurrentStep(step.id);
                  }}
                  className={cn(
                    'focus-clinical group flex items-center space-x-2.5',
                    isCurrent ? 'font-semibold text-[var(--color-clinical-400)]' : isCompleted ? 'font-semibold text-slate-text-primary' : 'font-medium text-slate-text-muted',
                  )}
                >
                  <div
                    className={cn(
                      'flex h-8 w-8 items-center justify-center rounded-full text-xs transition-colors duration-[var(--duration-fast)]',
                      isCurrent
                        ? 'bg-[var(--color-clinical-600)] text-white'
                        : isCompleted
                        ? 'bg-[var(--color-safety-success)] text-white'
                        : 'bg-slate-inset text-slate-text-muted',
                    )}
                  >
                    {isCompleted ? <Check className="h-4 w-4" aria-hidden="true" /> : step.id}
                  </div>
                  <span className="text-xs">{step.label}</span>
                </button>
                {step.id < 3 && <div className="mx-3 h-[2px] flex-1 bg-slate-border-subtle" />}
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Top API Error Banner */}
      {submitCaseMutation.isError && (
        <SafetyAlert level="critical" title="Clinical assessment submission error">
          {(submitCaseMutation.error as any)?.message || 'An unexpected error occurred while communicating with the decision engine.'}
        </SafetyAlert>
      )}

      {/* Form Steps */}
      <div className="min-h-[420px] rounded-[var(--radius-lg)] border border-slate-border bg-slate-surface p-6">
        {/* STEP 1: Demographics & Care Setting */}
        {currentStep === 1 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 1: Patient Demographics & Execution Mode</h3>
              <p className="text-xs text-slate-text-muted">Choose the plugins first. Their exposed schemas determine the clinical inputs shown next.</p>
            </div>

            <div className="space-y-3 rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/40 p-4">
              <div>
                <label className="block text-xs font-semibold text-slate-text-primary">Clinical Workflow Execution Strategy</label>
                <p className="mt-1 text-[11px] text-slate-text-muted">Automatic runs every available knowledge and prediction plugin. Custom Plugins lets you choose the set explicitly.</p>
              </div>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                {executionModes.map((mode) => {
                  const Icon = mode.icon;
                  const isSelected = (caseData.executionMode || 'AUTO') === mode.id;
                  return (
                    <button type="button" key={mode.id} onClick={() => setExecutionMode(mode.id)} className={`flex items-start gap-3 rounded-[var(--radius-md)] border p-3.5 text-left transition-all ${isSelected ? 'border-[var(--color-clinical-600)] bg-[var(--color-clinical-950)] ring-1 ring-[var(--color-clinical-500)]' : 'border-slate-border-subtle bg-slate-inset hover:border-slate-border'}`}>
                      <span className={`rounded-[var(--radius-md)] p-2 ${isSelected ? 'bg-[var(--color-clinical-600)] text-white' : 'bg-slate-inset text-slate-text-secondary'}`}><Icon className="h-4 w-4" /></span>
                      <span><span className="block text-xs font-semibold text-slate-text-primary">{mode.label}</span><span className="mt-0.5 block text-[11px] text-slate-text-muted">{mode.desc}</span></span>
                    </button>
                  );
                })}
              </div>
              {caseData.executionMode === 'USER_SELECTED' && (
                <div className="grid grid-cols-1 gap-2 pt-1 md:grid-cols-2">
                  {registeredPlugins.map((plugin) => {
                    const pluginId = plugin.backendId || plugin.id;
                    const selected = (caseData.pluginSelections || []).includes(pluginId);
                    return (
                      <label key={pluginId} className={`flex cursor-pointer items-start gap-2 rounded-[var(--radius-md)] border p-3 text-xs ${selected ? 'border-[var(--color-clinical-700)] bg-[var(--color-clinical-950)]/70' : 'border-slate-border-subtle bg-slate-inset'}`}>
                        <input type="checkbox" checked={selected} onChange={() => togglePluginSelection(pluginId)} className="mt-0.5 rounded text-[var(--color-clinical-500)]" />
                        <span><span className="block font-semibold text-slate-text-primary">{plugin.name}</span><span className="text-[10px] uppercase text-slate-text-muted">{plugin.category} plugin</span></span>
                      </label>
                    );
                  })}
                </div>
              )}
              <div className={`text-[11px] ${hasPluginMix ? 'text-[var(--color-safety-success)]' : 'text-[var(--color-safety-warning)]'}`}>
                Active: {activePlugins.length} plugin(s) | Knowledge: {activePlugins.filter((plugin) => plugin.category === 'knowledge').length} | Prediction: {activePlugins.filter((plugin) => plugin.category === 'prediction').length}
              </div>
              {fieldErrors.plugins && <p className="text-[11px] font-medium text-[var(--color-safety-critical)]">{fieldErrors.plugins}</p>}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">
                  Age (Years) <span className="text-[var(--color-safety-critical)]">*</span>
                </label>
                <input
                  type="number"
                  min={1}
                  max={125}
                  value={caseData.demographics.age || ''}
                  onChange={(e) => {
                    updateDemographics({ age: parseInt(e.target.value) || 0 });
                    if (fieldErrors.age) setFieldErrors(prev => ({ ...prev, age: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-[var(--radius-md)] border text-xs text-slate-text-primary focus:outline-none focus:ring-2 ${
                    fieldErrors.age
                      ? 'border-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] focus-clinical'
                      : 'border-slate-border-subtle bg-slate-inset focus-clinical'
                  }`}
                  required
                />
                {fieldErrors.age && (
                  <p className="text-[11px] text-[var(--color-safety-critical)] mt-1 font-medium">{fieldErrors.age}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Biological Sex</label>
                <select
                  value={caseData.demographics.sex}
                  onChange={(e) => updateDemographics({ sex: e.target.value as any })}
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Weight (kg)</label>
                <input
                  type="number"
                  value={caseData.demographics.weight || ''}
                  onChange={(e) => updateDemographics({ weight: parseFloat(e.target.value) || undefined })}
                  placeholder="e.g. 75"
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                />
              </div>
            </div>

            {/* Progressive Disclosure: Additional Context */}
            <div className="border border-slate-border rounded-[var(--radius-md)] overflow-hidden">
              <button
                type="button"
                onClick={() => setShowOptionalDetails(!showOptionalDetails)}
                className="w-full p-3 bg-slate-inset flex items-center justify-between text-xs font-semibold text-slate-text-secondary hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
              >
                <span>Additional Patient Context (Optional)</span>
                {showOptionalDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showOptionalDetails && (
                <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-canvas border-t border-slate-border">
                  <div>
                    <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Patient Full Name</label>
                    <input
                      type="text"
                      value={caseData.demographics.patientName || ''}
                      onChange={(e) => updateDemographics({ patientName: e.target.value })}
                      placeholder="Optional patient name"
                      className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Patient Hospital ID / MRN</label>
                    <input
                      type="text"
                      value={caseData.demographics.patientId || ''}
                      onChange={(e) => updateDemographics({ patientId: e.target.value })}
                      placeholder="e.g. PAT-94812"
                      className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                    />
                  </div>
                </div>
              )}
            </div>

          </div>
        )}

        {/* STEP 2: Plugin-generated clinical inputs */}
        {currentStep === 2 && activePlugins.length > 0 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 2: Plugin-Generated Clinical Inputs</h3>
              <p className="text-xs text-slate-text-muted">This form is assembled from the schemas exposed by the selected plugins.</p>
            </div>
            <PluginGeneratedForm plugins={activePlugins} caseData={caseData} onChange={updatePluginField} />
          </div>
        )}

        {/* Legacy grouped sections are unreachable through the plugin workflow. */}
        {false && currentStep === 2 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 2: Clinical Presentation & Vitals</h3>
              <p className="text-xs text-slate-text-muted">Document presenting infection diagnosis, symptom taxonomy, and objective vital metrics.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">
                  Primary Infection Diagnosis <span className="text-[var(--color-safety-critical)]">*</span>
                </label>
                <select
                  value={caseData.presentation.primaryDiagnosis}
                  onChange={(e) => {
                    updatePresentation({ primaryDiagnosis: e.target.value });
                    if (fieldErrors.primaryDiagnosis) setFieldErrors(prev => ({ ...prev, primaryDiagnosis: '' }));
                  }}
                  className={`w-full px-3 py-2 rounded-[var(--radius-md)] border text-xs text-slate-text-primary focus:outline-none focus:ring-2 ${
                    fieldErrors.primaryDiagnosis
                      ? 'border-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] focus-clinical'
                      : 'border-slate-border-subtle bg-slate-inset focus-clinical'
                  }`}
                >
                  {availableDiagnosis.map((diag) => (
                    <option key={diag} value={diag}>
                      {diag}
                    </option>
                  ))}
                </select>
                {fieldErrors.primaryDiagnosis && (
                  <p className="text-[11px] text-[var(--color-safety-critical)] mt-1 font-medium">{fieldErrors.primaryDiagnosis}</p>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Clinical Severity Tier</label>
                <select
                  value={caseData.presentation.severity}
                  onChange={(e) => updatePresentation({ severity: e.target.value as any })}
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                >
                  <option value="Non-severe">Non-severe (Outpatient Candidate)</option>
                  <option value="Moderate">Moderate (Inpatient Ward)</option>
                  <option value="Severe">Severe (High Dependency / Sepsis Risk)</option>
                  <option value="Critical/Sepsis">Critical / Septic Shock (ICU)</option>
                </select>
              </div>
            </div>

            {/* Presenting Symptoms Selection */}
            <div>
              <label className="block text-xs font-semibold text-slate-text-primary mb-2">Presenting Symptoms (Select all that apply)</label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {availableSymptoms.map((symp) => {
                  const isChecked = caseData.presentation.symptoms.includes(symp);
                  return (
                    <label
                      key={symp}
                      className={`flex items-center space-x-2 p-2.5 rounded-[var(--radius-md)] border text-xs cursor-pointer transition-all ${
                        isChecked
                          ? 'bg-[var(--color-clinical-950)] border-[var(--color-clinical-700)] font-semibold text-[var(--color-clinical-200)]'
                          : 'bg-slate-inset border-slate-border-subtle text-slate-text-secondary'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {
                          const updated = isChecked
                            ? caseData.presentation.symptoms.filter((s) => s !== symp)
                            : [...caseData.presentation.symptoms, symp];
                          updatePresentation({ symptoms: updated });
                        }}
                        className="rounded text-[var(--color-clinical-400)] focus-clinical"
                      />
                      <span>{symp}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Progressive Disclosure: Vitals & Anatomical Site */}
            <div className="border border-slate-border rounded-[var(--radius-md)] overflow-hidden">
              <button
                type="button"
                onClick={() => setShowOptionalVitals(!showOptionalVitals)}
                className="w-full p-3 bg-slate-inset flex items-center justify-between text-xs font-semibold text-slate-text-secondary hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
              >
                <span>Objective Vitals & Anatomical Focus (Optional)</span>
                {showOptionalVitals ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showOptionalVitals && (
                <div className="p-4 space-y-4 bg-slate-canvas border-t border-slate-border">
                  <div>
                    <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Infection Site / Anatomical Focus</label>
                    <input
                      type="text"
                      value={caseData.presentation.infectionSite || ''}
                      onChange={(e) => updatePresentation({ infectionSite: e.target.value })}
                      placeholder="e.g. Lower Respiratory Tract"
                      className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                    />
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-2.5 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
                      <label className="block text-[11px] font-semibold text-slate-text-muted mb-1">Body Temp (°C)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={caseData.presentation.vitals?.temperature || ''}
                        onChange={(e) =>
                          updatePresentation({
                            vitals: { ...caseData.presentation.vitals, temperature: parseFloat(e.target.value) || undefined },
                          })
                        }
                        className="w-full px-2 py-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas text-xs font-semibold text-slate-text-primary"
                      />
                    </div>
                    <div className="p-2.5 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
                      <label className="block text-[11px] font-semibold text-slate-text-muted mb-1">Heart Rate (BPM)</label>
                      <input
                        type="number"
                        value={caseData.presentation.vitals?.heartRate || ''}
                        onChange={(e) =>
                          updatePresentation({
                            vitals: { ...caseData.presentation.vitals, heartRate: parseInt(e.target.value) || undefined },
                          })
                        }
                        className="w-full px-2 py-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas text-xs font-semibold text-slate-text-primary"
                      />
                    </div>
                    <div className="p-2.5 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
                      <label className="block text-[11px] font-semibold text-slate-text-muted mb-1">Resp Rate (BPM)</label>
                      <input
                        type="number"
                        value={caseData.presentation.vitals?.respiratoryRate || ''}
                        onChange={(e) =>
                          updatePresentation({
                            vitals: { ...caseData.presentation.vitals, respiratoryRate: parseInt(e.target.value) || undefined },
                          })
                        }
                        className="w-full px-2 py-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas text-xs font-semibold text-slate-text-primary"
                      />
                    </div>
                    <div className="p-2.5 bg-slate-inset rounded-[var(--radius-md)] border border-slate-border-subtle">
                      <label className="block text-[11px] font-semibold text-slate-text-muted mb-1">SpO2 Sat (%)</label>
                      <input
                        type="number"
                        value={caseData.presentation.vitals?.oxygenSaturation || ''}
                        onChange={(e) =>
                          updatePresentation({
                            vitals: { ...caseData.presentation.vitals, oxygenSaturation: parseInt(e.target.value) || undefined },
                          })
                        }
                        className="w-full px-2 py-1 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-canvas text-xs font-semibold text-slate-text-primary"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 3: Laboratory & Renal Function */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 3: Laboratory Findings & Renal Clearance</h3>
              <p className="text-xs text-slate-text-muted">Serum biochemistry, inflammatory biomarkers, and microbiological cultures.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">
                  eGFR (mL/min/1.73m²)
                </label>
                <input
                  type="number"
                  value={caseData.laboratory.egfr || ''}
                  onChange={(e) => {
                    updateLaboratory({ egfr: parseFloat(e.target.value) || undefined });
                    if (fieldErrors.egfr) setFieldErrors(prev => ({ ...prev, egfr: '' }));
                  }}
                  placeholder="e.g. 55"
                  className={`w-full px-3 py-2 rounded-[var(--radius-md)] border text-xs text-slate-text-primary focus:outline-none focus:ring-2 ${
                    fieldErrors.egfr
                      ? 'border-[var(--color-safety-critical)] bg-[var(--color-safety-critical-bg)] focus-clinical'
                      : 'border-slate-border-subtle bg-slate-inset focus-clinical'
                  }`}
                />
                {fieldErrors.egfr ? (
                  <p className="text-[11px] text-[var(--color-safety-critical)] mt-1 font-medium">{fieldErrors.egfr}</p>
                ) : (
                  <span className="text-[10px] text-slate-text-muted mt-1 block">Critical threshold for renal dosing checks (&lt;30, &lt;60)</span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Serum Creatinine (mg/dL)</label>
                <input
                  type="number"
                  step="0.1"
                  value={caseData.laboratory.creatinine || ''}
                  onChange={(e) => updateLaboratory({ creatinine: parseFloat(e.target.value) || undefined })}
                  placeholder="e.g. 1.1"
                  className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                />
              </div>
            </div>

            {/* Progressive Disclosure: Inflammatory Biomarkers & Microbiology */}
            <div className="border border-slate-border rounded-[var(--radius-md)] overflow-hidden">
              <button
                type="button"
                onClick={() => setShowOptionalBiomarkers(!showOptionalBiomarkers)}
                className="w-full p-3 bg-slate-inset flex items-center justify-between text-xs font-semibold text-slate-text-secondary hover:bg-slate-inset-hover transition-colors duration-[var(--duration-fast)]"
              >
                <span>Inflammatory Biomarkers & Microbiology (Optional)</span>
                {showOptionalBiomarkers ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>

              {showOptionalBiomarkers && (
                <div className="p-4 space-y-4 bg-slate-canvas border-t border-slate-border">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-text-secondary mb-1">C-Reactive Protein (mg/L)</label>
                      <input
                        type="number"
                        value={caseData.laboratory.crp || ''}
                        onChange={(e) => updateLaboratory({ crp: parseFloat(e.target.value) || undefined })}
                        placeholder="e.g. 45"
                        className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-text-secondary mb-1">White Blood Count (10⁹/L)</label>
                      <input
                        type="number"
                        step="0.1"
                        value={caseData.laboratory.wbc || ''}
                        onChange={(e) => updateLaboratory({ wbc: parseFloat(e.target.value) || undefined })}
                        placeholder="e.g. 13.8"
                        className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Procalcitonin (ng/mL)</label>
                      <input
                        type="number"
                        step="0.01"
                        value={caseData.laboratory.procalcitonin || ''}
                        onChange={(e) => updateLaboratory({ procalcitonin: parseFloat(e.target.value) || undefined })}
                        placeholder="e.g. 0.60"
                        className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Suspected Pathogen</label>
                    <input
                      type="text"
                      value={caseData.laboratory.suspectedPathogen || ''}
                      onChange={(e) => updateLaboratory({ suspectedPathogen: e.target.value })}
                      placeholder="e.g. Streptococcus pneumoniae"
                      className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-text-secondary mb-1">Microbiology Culture & Gram Stain</label>
                    <textarea
                      rows={2}
                      value={caseData.laboratory.cultureResult || ''}
                      onChange={(e) => updateLaboratory({ cultureResult: e.target.value })}
                      placeholder="Document specimen type, Gram stain morphology, or preliminary blood culture alerts..."
                      className="w-full px-3 py-2 rounded-[var(--radius-md)] border border-slate-border-subtle bg-slate-inset text-xs text-slate-text-primary focus-clinical"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* STEP 4: Rules & Allergies */}
        {currentStep === 4 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 4: Clinical Safety Rules & Drug Allergies</h3>
              <p className="text-xs text-slate-text-muted">Document documented allergies, pregnancy/lactation status, and resistance risk factors.</p>
            </div>

            {/* Allergies Selection */}
            <div>
              <div className="mb-2 flex items-center justify-between">
                <label className="block text-xs font-semibold text-slate-text-primary">
                  Documented drug hypersensitivities & allergies
                </label>
                <label className="flex cursor-pointer items-center space-x-1.5 text-[11px] font-medium text-slate-text-secondary">
                  <input
                    type="checkbox"
                    checked={caseData.riskFactors.allergies.length === 0}
                    onChange={(e) => {
                      if (e.target.checked) updateRiskFactors({ allergies: [] });
                    }}
                    className="h-3.5 w-3.5 rounded text-[var(--color-safety-success)]"
                  />
                  <span>No known drug allergies (NKDA)</span>
                </label>
              </div>
              <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                {availableAllergies.map((allergy) => {
                  const isChecked = caseData.riskFactors.allergies.includes(allergy);
                  const isSevere = allergy.toLowerCase().includes('anaphylaxis');

                  return (
                    <label
                      key={allergy}
                      className={cn(
                        'flex cursor-pointer items-center space-x-2.5 rounded-[var(--radius-md)] border p-3 text-xs transition-colors duration-[var(--duration-fast)]',
                        isChecked
                          ? isSevere
                            ? 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)] font-semibold text-[var(--color-safety-critical)]'
                            : 'border-[var(--color-safety-warning-border)] bg-[var(--color-safety-warning-bg)] font-medium text-[var(--color-safety-warning)]'
                          : 'border-slate-border bg-slate-inset text-slate-text-secondary',
                      )}
                    >
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => {
                          const updated = isChecked
                            ? caseData.riskFactors.allergies.filter((a) => a !== allergy)
                            : [...caseData.riskFactors.allergies, allergy];
                          updateRiskFactors({ allergies: updated });
                        }}
                        className={cn('rounded', isSevere ? 'text-[var(--color-safety-critical)]' : 'text-[var(--color-safety-warning)]')}
                      />
                      <span>{allergy}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Allergy Safety Warning Notice if severe allergy selected */}
            {hasSeverePenicillin && (
              <SafetyAlert level="critical" title="Severe beta-lactam anaphylaxis flag active">
                The deterministic safety engine will strictly flag beta-lactams and carbapenems. Ensure
                non-beta-lactam alternatives (e.g. macrolides, respiratory fluoroquinolones) are prioritized.
              </SafetyAlert>
            )}

            {/* Risk Factor Toggles */}
            <div className="pt-2">
              <label className="mb-2 block text-xs font-semibold text-slate-text-primary">
                Physiological & antimicrobial risk factors
              </label>
              <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                <label className="flex cursor-pointer items-center justify-between rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-3">
                  <div>
                    <p className="text-xs font-semibold text-slate-text-primary">Pregnancy status</p>
                    <p className="text-[11px] text-slate-text-muted">Contraindicates fluoroquinolones & tetracyclines</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={caseData.riskFactors.isPregnant}
                    onChange={(e) => updateRiskFactors({ isPregnant: e.target.checked })}
                    className="h-4 w-4 rounded text-[var(--color-clinical-500)]"
                  />
                </label>

                <label className="flex cursor-pointer items-center justify-between rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-3">
                  <div>
                    <p className="text-xs font-semibold text-slate-text-primary">Lactation / breastfeeding</p>
                    <p className="text-[11px] text-slate-text-muted">Evaluates neonatal excretion safety</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={caseData.riskFactors.isLactating}
                    onChange={(e) => updateRiskFactors({ isLactating: e.target.checked })}
                    className="h-4 w-4 rounded text-[var(--color-clinical-500)]"
                  />
                </label>

                <label className="flex cursor-pointer items-center justify-between rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-3">
                  <div>
                    <p className="text-xs font-semibold text-slate-text-primary">Immunocompromised state</p>
                    <p className="text-[11px] text-slate-text-muted">Chemotherapy, biologicals, or organ transplant</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={caseData.riskFactors.isImmunocompromised}
                    onChange={(e) => updateRiskFactors({ isImmunocompromised: e.target.checked })}
                    className="h-4 w-4 rounded text-[var(--color-clinical-500)]"
                  />
                </label>

                <label className="flex cursor-pointer items-center justify-between rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-3">
                  <div>
                    <p className="text-xs font-semibold text-slate-text-primary">Prior antibiotic use (90 days)</p>
                    <p className="text-[11px] text-slate-text-muted">Elevates regional resistance weighting</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={caseData.riskFactors.priorAntibiotics90Days}
                    onChange={(e) => updateRiskFactors({ priorAntibiotics90Days: e.target.checked })}
                    className="h-4 w-4 rounded text-[var(--color-clinical-500)]"
                  />
                </label>
              </div>
            </div>
          </div>
        )}

        {/* STEP 5: Review & Run Pipeline */}
        {currentStep === 3 && (
          <div className="space-y-6 animate-in fade-in">
            <div>
              <h3 className="text-sm font-semibold text-slate-text-primary">Step 3: Review Clinical Case Profile & Pipeline Orchestration</h3>
              <p className="text-xs text-slate-text-muted">Confirm clinical parameters before dispatching to the Clinical Intelligence Pipeline.</p>
            </div>

            {/* Pre-flight Safety Check — surfaced above summary, not buried */}
            {hasSeverePenicillin && (
              <SafetyAlert level="critical" title="Pre-flight safety check: severe allergy on file">
                This case carries a documented severe beta-lactam allergy. The pipeline will exclude beta-lactams
                and carbapenems from candidate therapies.
              </SafetyAlert>
            )}

            {/* Summary Review Cards */}
            <div className="grid grid-cols-1 gap-4 text-xs md:grid-cols-3">
              <div className="space-y-2 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-4">
                <p className="flex items-center font-semibold text-slate-text-primary">
                  <User className="mr-1.5 h-3.5 w-3.5 text-[var(--color-clinical-400)]" aria-hidden="true" /> Patient demographics
                </p>
                <p className="text-slate-text-secondary">Name: <strong className="text-slate-text-primary">{caseData.demographics.patientName || 'Anonymous'}</strong></p>
                <p className="num-clinical text-slate-text-secondary">Age/Sex: <strong className="text-slate-text-primary">{caseData.demographics.age}y {caseData.demographics.sex}</strong></p>
                <p className="num-clinical text-slate-text-secondary">Weight: <strong className="text-slate-text-primary">{caseData.demographics.weight || 'Unspecified'} kg</strong></p>
              </div>

              <div className="space-y-2 rounded-[var(--radius-md)] border border-slate-border bg-slate-inset p-4">
                <p className="flex items-center font-semibold text-slate-text-primary">
                  <Activity className="mr-1.5 h-3.5 w-3.5 text-[var(--color-safety-success)]" aria-hidden="true" /> Presentation & vitals
                </p>
                <p className="text-slate-text-secondary">Indication: <strong className="text-slate-text-primary">{caseData.presentation.primaryDiagnosis}</strong></p>
                <p className="text-slate-text-secondary">Severity: <strong className="text-slate-text-primary">{caseData.presentation.severity}</strong></p>
                <p className="num-clinical text-slate-text-secondary">Temp / HR: <strong className="text-slate-text-primary">{caseData.presentation.vitals?.temperature || 37}°C / {caseData.presentation.vitals?.heartRate || 80} bpm</strong></p>
              </div>

              <div className={cn(
                'space-y-2 rounded-[var(--radius-md)] border p-4',
                hasSeverePenicillin ? 'border-[var(--color-safety-critical-border)] bg-[var(--color-safety-critical-bg)]/40' : 'border-slate-border bg-slate-inset',
              )}>
                <p className="flex items-center font-semibold text-slate-text-primary">
                  <ShieldAlert className="mr-1.5 h-3.5 w-3.5 text-[var(--color-safety-warning)]" aria-hidden="true" /> Safety constraints
                </p>
                <p className="num-clinical text-slate-text-secondary">eGFR: <strong className="text-slate-text-primary">{caseData.laboratory.egfr || caseData.demographics.creatinineClearance || 55} mL/min</strong></p>
                <p className="text-slate-text-secondary">Allergies: <strong className="text-slate-text-primary">{caseData.riskFactors.allergies.join(', ') || 'None documented'}</strong></p>
                <p className="text-slate-text-secondary">Pregnancy: <strong className="text-slate-text-primary">{caseData.riskFactors.isPregnant ? 'Yes (contraindication alert active)' : 'No'}</strong></p>
              </div>
            </div>

            {/* Pipeline Execution Strategy Overview */}
            <div className="space-y-2 rounded-[var(--radius-md)] border border-[var(--color-clinical-800)] bg-[var(--color-clinical-950)]/60 p-4 text-xs text-[var(--color-clinical-100)]">
              <div className="flex items-center space-x-2 font-semibold">
                <Sparkles className="h-4 w-4 text-[var(--color-clinical-400)]" aria-hidden="true" />
                <span>Active execution mode: {caseData.executionMode || 'AUTO'}</span>
              </div>
              <p className="text-[11px] leading-relaxed text-[var(--color-clinical-200)]">
                The Clinical Intelligence Pipeline will evaluate registered machine learning and guideline components
                to extract candidate therapies, evaluate deterministic Clinical Safety Rules (allergy, renal,
                pregnancy), and perform multi-criteria decision fusion with WHO AWaRe guidelines.
              </p>
              <p className="text-[10px] text-[var(--color-clinical-300)]/80">
                This information supports clinical decision-making; it does not replace clinician judgement.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons Footer */}
      <div className="flex items-center justify-between pt-2">
        <ClinicalButton
          variant="ghost"
          icon={ChevronLeft}
          onClick={handleBack}
          disabled={currentStep === 1 || submitCaseMutation.isPending}
        >
          Previous step
        </ClinicalButton>

        <div className="flex items-center space-x-3">
          <ClinicalButton variant="ghost" size="sm" onClick={resetCase} disabled={submitCaseMutation.isPending}>
            Reset form
          </ClinicalButton>

          {currentStep < 3 ? (
            <ClinicalButton variant="primary" onClick={handleNext} icon={undefined}>
              <span className="flex items-center gap-1.5">
                Next step
                <ChevronRight className="h-4 w-4" aria-hidden="true" />
              </span>
            </ClinicalButton>
          ) : (
            <div className="flex items-center gap-2">
              <ClinicalButton
                variant="primary"
                size="lg"
                onClick={handleSubmit}
                disabled={submitCaseMutation.isPending || !canSubmit}
                loading={submitCaseMutation.isPending}
                icon={submitCaseMutation.isPending ? undefined : Sparkles}
              >
                {submitCaseMutation.isPending ? 'Evaluating clinical case…' : 'Generate AI recommendation'}
              </ClinicalButton>

              {/* Server-orchestrated pipeline launch (if backend supports it) */}
              <ClinicalButton
                variant="secondary"
                size="lg"
                onClick={async () => {
                  try {
                    // Map frontend execution mode to pipeline mode; default to sync
                    const mode = 'sync' as const;
                    const payload = {
                      execution_mode: mode,
                      patient_id: caseData.demographics.patientId,
                      case_id: undefined,
                      plugin_selection: caseData.pluginSelections?.map((id) => ({ plugin_id: id })) ?? undefined,
                      input_payload: { case: caseData },
                      response_mode: 'full' as const,
                    };
                    const resp = await import('@/api').then(m => m.pipelineApi.executePipeline(payload));
                    if ((resp as any).status === 'accepted') {
                      useNotificationStore.getState().publish({
                        id: `pipeline:accepted:${(resp as any).execution_id}`,
                        level: 'info',
                        title: 'Pipeline accepted',
                        message: `Execution ${(resp as any).execution_id} is available in Workflow Manager.`,
                      });
                    } else {
                      const rec = (resp as any).recommendation || (resp as any);
                      useNotificationStore.getState().publish({
                        id: `pipeline:response:${Date.now()}`,
                        level: 'success',
                        title: 'Pipeline response received',
                        message: String(rec?.primary_recommendation?.antibiotic_name ?? 'Recommendation data is available.'),
                      });
                    }
                  } catch (e) {
                    useNotificationStore.getState().publish({
                      id: `pipeline:failed:${Date.now()}`,
                      level: 'critical',
                      title: 'Pipeline execution failed',
                      message: (e as Error).message,
                    });
                  }
                }}
              >
                Run server pipeline
              </ClinicalButton>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
