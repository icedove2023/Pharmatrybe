import React, { useState, useEffect } from 'react';
import { getPatientById, getPatientHistory, searchPatients } from '@/api/patientsApi';
import { ApiClientError } from '@/api/client';
import { useAuthStore } from '@/stores/authStore';

interface Props {
  patientId?: string;
}

export default function PatientHistoryView({ patientId: initialPatientId }: Props) {
  const [patientId, setPatientId] = useState<string | undefined>(initialPatientId);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [patient, setPatient] = useState<any | null>(null);
  const [history, setHistory] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchResults, setSearchResults] = useState<any[] | null>(null);

  useEffect(() => {
    if (!patientId) return;
    setLoading(true);
    setError(null);
    setPatient(null);
    setHistory(null);
    (async () => {
      try {
          const p = await getPatientById(patientId);
        if (!p) {
          setError('This patient history is not visible to this account.');
          setLoading(false);
          return;
        }
        setPatient(p);

          const h = await getPatientHistory(patientId);
        if (!h) {
          setHistory(null);
          setError('No patient history is available for this account.');
        } else {
          setHistory(h);
        }
      } catch (err: any) {
        // unexpected errors
        setError(err?.message || 'Failed to load patient');
      } finally {
        setLoading(false);
      }
    })();
  }, [patientId]);

  async function handleSearch(e?: React.FormEvent) {
    e?.preventDefault();
    if (!query) return;
    setLoading(true);
    setError(null);
    setSearchResults(null);
    try {
        const results = await searchPatients(query);
      setSearchResults(results);
    } catch (err: any) {
      if (err instanceof ApiClientError && (err.status === 404 || err.status === 501)) {
        setError('Patient search is not currently available from the backend.');
      } else {
        setError(err?.message || 'Failed to search patients');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4">
      <h1 className="text-2xl font-semibold mb-4">Patient History</h1>

      {!patientId && (
        <form onSubmit={handleSearch} className="mb-4">
          <label className="block mb-2">Search patient</label>
          <div className="flex gap-2">
            <input
              className="border rounded px-3 py-2 flex-1"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by name, identifier..."
            />
            <button type="submit" className="bg-[var(--color-safety-info-bg)] text-white px-4 py-2 rounded">Search</button>
          </div>
        </form>
      )}

      {loading && <div>Loading...</div>}

      {error && (
        <div className="bg-[var(--color-safety-warning-bg)] border-l-4 border-[var(--color-safety-warning-border)] p-3 mb-4">{error}</div>
      )}

      {searchResults && (
        <div className="mb-4">
          <h2 className="font-medium mb-2">Search results</h2>
          <ul className="space-y-2">
            {searchResults.map((s) => (
              <li key={s.id} className="p-2 border rounded hover:shadow cursor-pointer" onClick={() => setPatientId(s.id)}>
                <div className="font-semibold">{s.name || 'Patient not named'}</div>
                <div className="text-sm text-muted">{s.date_of_birth || ''} {s.sex ? `· ${s.sex}` : ''}</div>
              </li>
            ))}
          </ul>
        </div>
      )}

      {patient && (
        <div className="bg-white border rounded p-4 mb-4">
          <div className="flex items-start gap-4">
            <div>
              <div className="text-lg font-semibold">{patient.name || 'Patient not named'}</div>
              <div className="text-sm text-muted">{patient.date_of_birth || ''} {patient.sex ? `· ${patient.sex}` : ''}</div>
            </div>
          </div>
        </div>
      )}

      {/* History placeholder: do not fabricate timeline — show message when backend lacks the endpoint */}
      {patient && history && (
        <div>
          <h2 className="text-lg font-medium mb-2">Longitudinal history</h2>
          <pre className="bg-gray-50 p-3 rounded overflow-auto">{JSON.stringify(history, null, 2)}</pre>
        </div>
      )}

      {patient && !history && (
        <div className="p-4 bg-gray-50 border rounded">
          <p className="mb-2">A dedicated longitudinal patient history is not currently available from the backend.</p>
          <p className="text-sm text-muted">The Patient History screen has been implemented per the product architecture, but the server must provide a /patients or /patients/{'{id}'}/history endpoint for full data. Until then, available case-level information can be viewed from Clinical Cases.</p>
        </div>
      )}

    </div>
  );
}
