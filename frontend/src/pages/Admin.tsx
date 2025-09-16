import React, { useEffect, useState } from 'react';

const API_BASE = (import.meta as any).env?.VITE_API_URL || '/api';

const Admin: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/admin/overview`);
        const json = await res.json();
        setData(json);
      } catch (e: any) {
        setError(e?.message || 'Failed to load admin overview');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Admin Overview</h1>
      {loading && <div>Loading...</div>}
      {error && <div className="text-red-600">{error}</div>}
      {data && (
        <div className="space-y-6">
          <section className="bg-white rounded-md border p-4">
            <h2 className="font-semibold mb-2">Keys</h2>
            <ul className="text-sm">
              {Object.entries(data.keys || {}).map(([k, v]: any) => (
                <li key={k} className="flex justify-between border-b py-1">
                  <span>{k}</span>
                  <span className={v ? 'text-green-600' : 'text-red-600'}>
                    {String(v)}
                  </span>
                </li>
              ))}
            </ul>
          </section>

          <section className="bg-white rounded-md border p-4">
            <h2 className="font-semibold mb-2">Orchestrator</h2>
            <div className="text-sm">
              Available:{' '}
              <span
                className={
                  data?.orchestrator?.available
                    ? 'text-green-600'
                    : 'text-red-600'
                }
              >
                {String(data?.orchestrator?.available)}
              </span>
            </div>
          </section>

          <section className="bg-white rounded-md border p-4">
            <h2 className="font-semibold mb-2">Providers</h2>
            <div className="text-sm mb-2">
              System: {data?.providers?._system?.status || 'unknown'}
            </div>
            <div className="text-sm mb-2">
              Available providers:{' '}
              {(data?.providers?._system?.available_providers || []).join(
                ', '
              ) || 'none'}
            </div>
            <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-64">
              {JSON.stringify(data.providers, null, 2)}
            </pre>
          </section>
        </div>
      )}
    </div>
  );
};

export default Admin;
