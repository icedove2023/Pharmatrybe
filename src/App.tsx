import React, { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { useSettingsStore } from '@/stores/settingsStore';
import { AppLayout } from '@/components/layout/AppLayout';
import { DashboardView } from '@/components/dashboard/DashboardView';
import { AssessmentWizard } from '@/components/assessment/AssessmentWizard';
import { RecommendationView } from '@/components/recommendation/RecommendationView';
import { ExplainabilityView } from '@/components/explainability/ExplainabilityView';
import { WhoExplorerView } from '@/components/who/WhoExplorerView';
import { SoarExplorerView } from '@/components/soar/SoarExplorerView';
import { ArmdExplorerView } from '@/components/armd/ArmdExplorerView';
import { PluginExplorerView } from '@/components/plugins/PluginExplorerView';
import { WorkflowManagerView } from '@/components/plugins/WorkflowManagerView';
import { isPluginRoute, pluginIdFromRoute } from '@/lib/pluginNav';
import { PatientHistoryView } from '@/components/patient/PatientHistoryView';
import { AdminDashboardView } from '@/components/admin/AdminDashboardView';
import { GovernanceTelemetryView } from '@/components/admin/GovernanceTelemetryView';
import { SettingsView } from '@/components/settings/SettingsView';
import { TelemetryDashboard } from '@/components/telemetry/TelemetryDashboard';
import { PluginGovernanceView } from '@/components/admin/PluginGovernanceView';
import { LoginForm } from '@/components/auth/LoginForm';
import { LandingPage } from '@/components/auth/LandingPage';
import { HospitalRegistrationForm } from '@/components/auth/HospitalRegistrationForm';
import { InvitationAcceptanceForm } from '@/components/auth/InvitationAcceptanceForm';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { ClinicalButton } from '@/components/ui/ClinicalButton';
import { SafetyAlert } from '@/components/ui/SafetyAlert';
import { ArrowLeft, Sparkles, Pill } from 'lucide-react';
import { BreadcrumbItem } from '@/components/common/Breadcrumbs';

export default function App() {
  const { user, status, initialize } = useAuthStore();
  const queryClient = useQueryClient();
  const { loadSettings } = useSettingsStore();

  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [activeCaseId, setActiveCaseId] = useState<string>('CASE-812901');
  const [recSubTab, setRecSubTab] = useState<'recommendation' | 'explainability'>('recommendation');
  const [authView, setAuthView] = useState<'landing' | 'login' | 'register'>('landing');
  const invitationToken = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('token') : null;

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;
    void initialize(queryClient).then((cleanup) => { unsubscribe = cleanup; });
    loadSettings();
    return () => unsubscribe?.();
  }, [initialize, loadSettings, queryClient]);

  // Compute breadcrumbs dynamically based on activeTab
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    switch (activeTab) {
      case 'assessment':
        return [
          { label: 'Clinical Operations' },
          { label: 'Case Assessment Wizard', active: true },
        ];
      case 'recommendation':
        return [
          { label: 'Clinical Decision Support' },
          {
            label: recSubTab === 'recommendation' ? 'Primary Recommendations' : 'SHAP Explainability Tree',
            active: true,
          },
        ];
      case 'patients':
        return [
          { label: 'Clinical Operations' },
          { label: 'Patient Directory', active: true },
        ];
      case 'who':
        return [
          { label: 'Guidelines & Knowledge' },
          { label: 'WHO AWaRe Knowledge Base', active: true },
        ];
      case 'soar':
        return [
          { label: 'Surveillance & Prediction' },
          { label: 'SOAR Surveillance Prediction', active: true },
        ];
      case 'armd':
        return [
          { label: 'Surveillance & Prediction' },
          { label: 'ARMD Resistance Prediction', active: true },
        ];
      case 'telemetry':
        return [
          { label: 'Governance' },
          { label: 'Plugin Registry & Model Telemetry', active: true },
        ];
      case 'admin':
        return [
          { label: 'professionals & invitations' },
          { label: 'Professionals & invitations', active: true },
        ];
      case 'governance-telemetry':
        return [
          { label: 'Governance' },
          { label: 'System health & governance', active: true },
        ];
      case 'plugin-governance':
        return [
          { label: 'Governance' },
          { label: 'Plugin Governance', active: true },
        ];
      case 'settings':
        return [
          { label: 'Governance' },
          { label: 'Clinical Preferences & Dosing', active: true },
        ];
      case 'dashboard':
        return [{ label: 'Clinical Operations' }, { label: 'Dashboard', active: true }];
      default:
        if (isPluginRoute(activeTab)) {
          return [{ label: 'Knowledge & surveillance' }, { label: 'Plugin explorer', active: true }];
        }
        return [{ label: 'Page not found', active: true }];
    }
  };

  if (status === 'loading') {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-slate-canvas text-slate-text-primary">
        <div className="flex flex-col items-center space-y-4">
          <div className="flex h-12 w-12 animate-pulse items-center justify-center rounded-[var(--radius-lg)] bg-[var(--color-clinical-600)] shadow-lg">
            <Pill className="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <div className="flex flex-col items-center space-y-1.5 text-center">
            <h2 className="text-sm font-semibold text-slate-text-primary">PharmaTrybe CDSS</h2>
            <p className="text-xs text-slate-text-muted">Verifying session…</p>
          </div>
        </div>
      </div>
    );
  }

  if (invitationToken) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-canvas p-3 sm:p-6 lg:p-8">
        <InvitationAcceptanceForm token={invitationToken} />
      </div>
    );
  }

  if (status === 'unauthenticated' || !user) {
    if (authView === 'landing') {
      return (
        <LandingPage
          onSignIn={() => setAuthView('login')}
          onRegisterHospital={() => setAuthView('register')}
        />
      );
    }
    if (authView === 'register') {
      return (
        <div className="flex min-h-screen items-center justify-center bg-slate-canvas p-3 sm:p-6 lg:p-8">
          <HospitalRegistrationForm
            onBackToLanding={() => setAuthView('landing')}
            onSwitchToSignIn={() => setAuthView('login')}
          />
        </div>
      );
    }
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-canvas p-3 sm:p-6 lg:p-8">
        <LoginForm
          onBackToLanding={() => setAuthView('landing')}
          onSwitchToRegister={() => setAuthView('register')}
        />
      </div>
    );
  }

  return (
    <AppLayout
      activeTab={activeTab}
      onSelectTab={(tab) => setActiveTab(tab)}
      breadcrumbs={getBreadcrumbs()}
    >
      {/* Dashboard View */}
      {activeTab === 'dashboard' && (
        <DashboardView onNavigateTab={(t) => setActiveTab(t)} />
      )}

      {/* Workflow Manager */}
      {activeTab === 'workflow' && (
        <AuthGuard
          requiredPermission="pipeline:execute"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <WorkflowManagerView caseId={activeCaseId} patientId={undefined} />
        </AuthGuard>
      )}

      {/* Clinical Assessment Wizard */}
      {activeTab === 'assessment' && (
        <AuthGuard
          requiredPermission="cases:create"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <AssessmentWizard
            onCaseSubmitted={(caseId) => {
              setActiveCaseId(caseId);
              setRecSubTab('recommendation');
              setActiveTab('recommendation');
            }}
          />
        </AuthGuard>
      )}

      {/* Decision Support & Recommendation View */}
      {activeTab === 'recommendation' && (
        <AuthGuard
          requiredPermission="recommendations:view"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <div className="space-y-4">
            {/* Sub-tab Switcher between Recommendation & Explainability */}
            <div className="flex items-center space-x-2 bg-white dark:bg-slate-canvas border border-slate-border dark:border-slate-border p-1.5 rounded-2xl w-fit shadow-xs">
              <button
                onClick={() => setRecSubTab('recommendation')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                  recSubTab === 'recommendation'
                    ? 'bg-[var(--color-safety-info-bg)] text-white shadow-xs'
                    : 'text-slate-text-secondary dark:text-slate-text-muted hover:text-slate-text-primary dark:hover:text-slate-text-primary'
                }`}
              >
                Primary Recommendation Package
              </button>
              <button
                onClick={() => setRecSubTab('explainability')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer ${
                  recSubTab === 'explainability'
                    ? 'bg-[var(--color-safety-info-bg)] text-white shadow-xs'
                    : 'text-slate-text-secondary dark:text-slate-text-muted hover:text-slate-text-primary dark:hover:text-slate-text-primary'
                }`}
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Explainability Deep Dive (SHAP & Reasoning Tree)</span>
              </button>
            </div>

            {recSubTab === 'recommendation' ? (
              <RecommendationView
                caseId={activeCaseId}
                onOpenExplainability={() => setRecSubTab('explainability')}
              />
            ) : (
              <ExplainabilityView caseId={activeCaseId} />
            )}
          </div>
        </AuthGuard>
      )}

      {/* WHO Explorer */}
      {activeTab === 'who' && <WhoExplorerView />}

      {/* SOAR Explorer */}
      {activeTab === 'soar' && <SoarExplorerView />}

      {/* ARMD ML Explorer */}
      {activeTab === 'armd' && <ArmdExplorerView />}

      {/* Generic explorer for any other registered plugin without a dedicated UI */}
      {isPluginRoute(activeTab) && <PluginExplorerView pluginId={pluginIdFromRoute(activeTab)} />}

      {/* Patient History */}
      {activeTab === 'patients' && <PatientHistoryView />}

      {/* Plugin Registry & Model Telemetry */}
      {activeTab === 'telemetry' && (
        <AuthGuard
          requiredPermission="plugins:configure"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <TelemetryDashboard caseId={activeCaseId} />
        </AuthGuard>
      )}

      {activeTab === 'plugin-governance' && (
        <AuthGuard
          requiredPermission="plugins:configure"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <PluginGovernanceView />
        </AuthGuard>
      )}

      {/* Admin Dashboard */}
      {activeTab === 'admin' && (
        <AuthGuard
          requiredPermission="professionals:manage"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <AdminDashboardView />
        </AuthGuard>
      )}

      {activeTab === 'governance-telemetry' && (
        <AuthGuard
          requiredPermission="professionals:manage"
          fallbackRoute="dashboard"
          onNavigate={(t) => setActiveTab(t)}
        >
          <GovernanceTelemetryView />
        </AuthGuard>
      )}

      {/* Settings View */}
      {activeTab === 'settings' && <SettingsView />}

      {/* Unknown route fallback */}
      {![
        'dashboard',
        'workflow',
        'assessment',
        'recommendation',
        'who',
        'soar',
        'armd',
        'patients',
        'telemetry',
        'admin',
        'governance-telemetry',
        'plugin-governance',
        'settings',
      ].includes(activeTab) && !isPluginRoute(activeTab) && (
        <div className="mx-auto max-w-2xl py-8">
          <SafetyAlert level="info" title="Page not found">
            This workspace does not contain the requested view. Return to the clinical dashboard to continue.
            <div className="mt-4">
              <ClinicalButton icon={ArrowLeft} onClick={() => setActiveTab('dashboard')}>
                Back to dashboard
              </ClinicalButton>
            </div>
          </SafetyAlert>
        </div>
      )}
    </AppLayout>
  );
}
