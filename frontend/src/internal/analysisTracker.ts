/*
  Internal-only "no-bad-answer" analysis tracker.
  - Aggregates suggestions from model outputs
  - Deduplicates with simple similarity
  - Produces confidence per merged item
  - Persists to localStorage (private, non-UI)
*/

export interface AnalysisItem {
  id: string;
  text: string;
  sources: string[]; // model names or identifiers
  mergedIds: string[];
  summary: string;
  confidence: number; // 0..1
  tags?: string[];
  createdAt: string; // ISO
}

export interface NoBadAnswerPayload {
  items: AnalysisItem[];
  generatedAt: string; // ISO
  prompt?: string;
}

const STORAGE_NAMESPACE = "ultra_internal_no_bad_answer";

function safeLog(...args: any[]) {
  try {
    // eslint-disable-next-line no-console
    console.debug("[internal]", ...args);
  } catch (_) {}
}

function normalizeText(input: string): string {
  return (input || "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .replace(/[\-•*]+\s*/g, " ")
    .trim();
}

function jaccardSimilarity(a: string, b: string): number {
  const aTokens = new Set(a.split(" "));
  const bTokens = new Set(b.split(" "));
  if (aTokens.size === 0 && bTokens.size === 0) return 1;
  let intersection = 0;
  for (const t of aTokens) if (bTokens.has(t)) intersection++;
  const union = aTokens.size + bTokens.size - intersection;
  return union === 0 ? 0 : intersection / union;
}

function summarizeCluster(texts: string[]): string {
  if (texts.length === 0) return "";
  // Simple summary: first sentence of the longest item
  const longest = texts.slice().sort((x, y) => y.length - x.length)[0];
  const firstSentence = longest.split(/(?<=[.!?])\s+/)[0];
  return firstSentence.length > 200 ? longest.slice(0, 200) + "…" : firstSentence;
}

function computeConfidence(votes: number, agreement: number): number {
  // Heuristic: votes (0.0–1.0) and agreement (0.0–1.0)
  const votesScore = Math.min(1, votes / 5); // saturate at 5 sources
  const agreementScore = agreement; // direct
  const base = 0.25;
  return Math.max(0, Math.min(1, base + 0.5 * votesScore + 0.25 * agreementScore));
}

export function buildNoBadAnswer(rawSuggestions: Array<{ text: string; source?: string }>, prompt?: string): NoBadAnswerPayload {
  const suggestions = (rawSuggestions || []).filter(s => s && s.text && s.text.trim().length > 0);
  const clusters: Array<{ texts: string[]; sources: string[]; normalized: string[] }> = [];

  const SIM_THRESHOLD = 0.82;

  for (const s of suggestions) {
    const norm = normalizeText(s.text);
    let placed = false;
    for (const c of clusters) {
      // Compare to cluster representative (first normalized)
      const rep = c.normalized[0] || "";
      const sim = jaccardSimilarity(rep, norm);
      if (sim >= SIM_THRESHOLD) {
        c.texts.push(s.text);
        c.sources.push(s.source || "unknown");
        c.normalized.push(norm);
        placed = true;
        break;
      }
    }
    if (!placed) clusters.push({ texts: [s.text], sources: [s.source || "unknown"], normalized: [norm] });
  }

  const items: AnalysisItem[] = clusters.map((c, idx) => {
    const id = `nba_${Date.now()}_${idx}`;
    const summary = summarizeCluster(c.texts);
    // Agreement as average pairwise similarity to representative
    const rep = c.normalized[0] || "";
    const sims = c.normalized.map(n => jaccardSimilarity(rep, n));
    const agreement = sims.length ? sims.reduce((a, b) => a + b, 0) / sims.length : 0;
    const confidence = computeConfidence(c.sources.length, agreement);
    return {
      id,
      text: summary,
      sources: Array.from(new Set(c.sources)),
      mergedIds: c.normalized.map((_, i) => `${id}_m${i}`),
      summary,
      confidence,
      createdAt: new Date().toISOString(),
    };
  });

  return {
    items,
    generatedAt: new Date().toISOString(),
    prompt,
  };
}

export function persistNoBadAnswer(payload: NoBadAnswerPayload): void {
  try {
    const key = `${STORAGE_NAMESPACE}:${payload.generatedAt}`;
    localStorage.setItem(key, JSON.stringify(payload));
    localStorage.setItem(`${STORAGE_NAMESPACE}:latest`, key);
    safeLog("no-bad-answer stored", key, payload.items.length, "items");
  } catch (err) {
    safeLog("persist error", err);
  }
}

export function getLatestNoBadAnswer(): NoBadAnswerPayload | null {
  try {
    const latestKey = localStorage.getItem(`${STORAGE_NAMESPACE}:latest`);
    if (!latestKey) return null;
    const raw = localStorage.getItem(latestKey);
    return raw ? (JSON.parse(raw) as NoBadAnswerPayload) : null;
  } catch (err) {
    safeLog("read latest error", err);
    return null;
  }
}

// Internal analyses registry (private): definitions, prompt templates, expected outputs
export type AnalysisRole = 'negotiator' | 'mediator' | 'devils_advocate' | 'no_bad_idea';

export interface AnalysisDefinition {
  id: AnalysisRole;
  displayName: string;
  objective: string;
  promptTemplate: string; // Internal system prompt used to drive this analysis
  expectedOutputs: string[]; // Headings/sections we expect back
}

const REGISTRY_NS = "ultra_internal_analyses_registry";

export function getAnalysesRegistry(): Record<AnalysisRole, AnalysisDefinition> {
  try {
    const raw = localStorage.getItem(REGISTRY_NS);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  const defaults: Record<AnalysisRole, AnalysisDefinition> = {
    negotiator: {
      id: 'negotiator',
      displayName: 'Negotiator',
      objective: 'Reconcile competing positions into a mutually beneficial plan with explicit trade-offs.',
      promptTemplate:
        "You are a master negotiator. Given multiple model proposals, identify conflicts, propose concessions, and synthesize a win-win plan. Output concise, actionable steps and deal terms.",
      expectedOutputs: [
        'Positions Summary',
        'Conflicts & Constraints',
        'Proposed Concessions',
        'Final Negotiated Plan',
        'Risks & Mitigations',
      ],
    },
    mediator: {
      id: 'mediator',
      displayName: 'Mediator',
      objective: 'Facilitate consensus across divergent proposals while preserving key intents.',
      promptTemplate:
        "You are a neutral mediator. Cluster overlapping ideas, surface shared ground, and produce a consensus plan preserving core intents. Be transparent about dissent.",
      expectedOutputs: [
        'Shared Ground',
        'Points of Divergence',
        'Consensus Plan',
        'Unresolved Items',
      ],
    },
    devils_advocate: {
      id: 'devils_advocate',
      displayName: "Devil's Advocate",
      objective: 'Stress-test assumptions and identify failures, edge cases, and counterarguments.',
      promptTemplate:
        "Adopt a rigorous devil's advocate stance. Challenge assumptions, find edge cases, quantify impact, and propose tests or safeguards.",
      expectedOutputs: [
        'Key Assumptions',
        'Counterarguments & Failure Modes',
        'Impact Assessment',
        'Tests & Safeguards',
      ],
    },
    no_bad_idea: {
      id: 'no_bad_idea',
      displayName: 'No Bad Idea (Convergence/Divergence)',
      objective: 'Include all suggestions; dedupe; label confidence; show divergent branches and convergence options.',
      promptTemplate:
        "Include every suggestion without discarding. Dedupe near-duplicates. Group into divergent branches, then propose convergence options. Assign a 0-1 confidence to each consolidated idea (based on support, agreement, clarity).",
      expectedOutputs: [
        'All Suggestions (Deduped)',
        'Divergent Branches',
        'Convergence Options',
        'Per-Item Confidence (0-1)',
      ],
    },
  };
  try {
    localStorage.setItem(REGISTRY_NS, JSON.stringify(defaults));
  } catch (_) {}
  return defaults;
}

export function setAnalysesRegistry(reg: Record<AnalysisRole, AnalysisDefinition>): void {
  try {
    localStorage.setItem(REGISTRY_NS, JSON.stringify(reg));
  } catch (_) {}
}

function extractSuggestions(orchestratorResult: any): Array<{ text: string; source?: string }> {
  if (!orchestratorResult) return [];
  // Prefer explicit arrays if present
  const direct: Array<{ text: string; source?: string }> = [];
  if (Array.isArray(orchestratorResult?.suggestions)) {
    for (const s of orchestratorResult.suggestions) {
      if (typeof s === "string") direct.push({ text: s });
      else if (s && typeof s.text === "string") direct.push({ text: s.text, source: s.source });
    }
  }
  if (direct.length) return direct;

  // Try model_responses: { model: string, text: string }[]
  if (Array.isArray(orchestratorResult?.model_responses)) {
    for (const r of orchestratorResult.model_responses) {
      if (r && typeof r.text === "string") direct.push({ text: r.text, source: r.model });
    }
    if (direct.length) return direct;
  }

  // Fallback: attempt to split final_result into bullet-like suggestions
  const fr: string | undefined = orchestratorResult?.final_result;
  if (typeof fr === "string" && fr.trim().length > 0) {
    const lines = fr.split(/\n+/);
    for (const line of lines) {
      const trimmed = line.trim();
      if (/^(\-|\*|\d+\.|\u2022)\s+/.test(trimmed) || trimmed.length > 40) {
        // Treat as a candidate suggestion
        direct.push({ text: trimmed });
      }
    }
  }
  return direct;
}

export function captureNoBadAnswerFromOrchestrator(
  orchestratorResult: any,
  selectedModels: string[] | undefined,
  prompt?: string
): void {
  try {
    const raw = extractSuggestions(orchestratorResult);
    // Map sources to known selected models if missing
    const normalized = raw.map((r, i) => ({
      text: r.text,
      source: r.source || (selectedModels && selectedModels[i % (selectedModels.length || 1)]) || "unknown",
    }));
    const payload = buildNoBadAnswer(normalized, prompt);
    persistNoBadAnswer(payload);
  } catch (err) {
    safeLog("capture error", err);
  }
}


