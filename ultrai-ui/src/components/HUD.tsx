import React, { useEffect, useState } from 'react';
import { fetchStatus, OrchestratorStatus } from '../lib/orchestrator';

export default function HUD() {
  const [s, setS] = useState<OrchestratorStatus | null>(null);
  
  useEffect(() => {
    const id = setInterval(async () => setS(await fetchStatus()), 3000);
    return () => clearInterval(id);
  }, []);
  
  return (
    <div className="flex gap-2 text-xs">
      {s && (
        <>
          <span>{s.online ? 'online' : 'offline'}</span>
          <span>pattern: {s.pattern}</span>
        </>
      )}
    </div>
  );
}