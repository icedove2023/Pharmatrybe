import { createFileRoute, ClientOnly } from "@tanstack/react-router";
import { Suspense, lazy } from "react";
import { Pill } from "lucide-react";

// The CDSS application is a fully client-side SPA (Supabase session, zustand
// stores, browser-only theming), so it is mounted after hydration only.
const App = lazy(() => import("@/App"));

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "PharmaTrybe CDSS — Clinical Decision Support" },
      {
        name: "description",
        content:
          "Explainable antimicrobial clinical decision support for hospitals: assessments, recommendations, surveillance and governance.",
      },
      { property: "og:title", content: "PharmaTrybe CDSS — Clinical Decision Support" },
      {
        property: "og:description",
        content:
          "Explainable antimicrobial clinical decision support for hospitals: assessments, recommendations, surveillance and governance.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

function AppBootScreen() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-slate-canvas text-slate-text-primary">
      <div className="flex flex-col items-center space-y-4">
        <div className="flex h-12 w-12 animate-pulse items-center justify-center rounded-[var(--radius-lg)] bg-[var(--color-clinical-600)] shadow-clinical-md">
          <Pill className="h-6 w-6 text-white" aria-hidden="true" />
        </div>
        <div className="flex flex-col items-center space-y-1.5 text-center">
          <h2 className="text-sm font-semibold text-slate-text-primary">PharmaTrybe CDSS</h2>
          <p className="text-xs text-slate-text-muted">Loading clinical workspace…</p>
        </div>
      </div>
    </div>
  );
}

function Index() {
  return (
    <ClientOnly fallback={<AppBootScreen />}>
      <Suspense fallback={<AppBootScreen />}>
        <App />
      </Suspense>
    </ClientOnly>
  );
}
