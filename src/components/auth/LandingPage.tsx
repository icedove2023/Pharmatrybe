import React from 'react';
import { motion, useReducedMotion } from 'motion/react';
import { Pill, Building2, UserCheck } from 'lucide-react';
import { ClinicalButton } from '@/components/ui/ClinicalButton';

interface LandingPageProps {
  onSignIn: () => void;
  onRegisterHospital: () => void;
}

export function LandingPage({ onSignIn, onRegisterHospital }: LandingPageProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="flex min-h-screen flex-col bg-slate-canvas">
      {/* Header */}
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-border-subtle px-6">
        <div className="flex items-center space-x-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-[var(--radius-md)] bg-[var(--color-clinical-600)]">
            <Pill className="h-5 w-5 text-white" aria-hidden="true" />
          </div>
          <span className="text-sm font-semibold tracking-tight text-slate-text-primary">PharmaTrybe CDSS</span>
        </div>
        <ClinicalButton variant="outline" size="sm" onClick={onSignIn}>
          Sign in
        </ClinicalButton>
      </header>

      {/* Hero */}
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center px-6 py-16 text-center">
        <motion.h1
          initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.05, ease: [0.2, 0.8, 0.2, 1] }}
          className="max-w-3xl text-3xl font-semibold leading-tight tracking-tight text-slate-text-primary sm:text-4xl"
        >
          Antimicrobial stewardship guidance clinicians can trust and verify.
        </motion.h1>

        <motion.p
          initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.1, ease: [0.2, 0.8, 0.2, 1] }}
          className="mt-4 max-w-2xl text-sm leading-relaxed text-slate-text-secondary"
        >
          PharmaTrybe combines WHO AWaRe guideline knowledge with resistance-prediction models and a
          deterministic clinical safety engine. Every recommendation shows its reasoning. The clinician always
          makes the final call.
        </motion.p>

        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: 0.15, ease: [0.2, 0.8, 0.2, 1] }}
          className="mt-8 flex flex-col gap-3 sm:flex-row"
        >
          <ClinicalButton variant="primary" size="lg" icon={Building2} onClick={onRegisterHospital}>
            Register your hospital
          </ClinicalButton>
          <ClinicalButton variant="secondary" size="lg" icon={UserCheck} onClick={onSignIn}>
            Sign in to your account
          </ClinicalButton>
        </motion.div>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-border-subtle px-6 py-4 text-center text-[11px] text-slate-text-muted">
        This information supports clinical decision-making; it does not replace clinician judgement.
      </footer>
    </div>
  );
}
