import findingsSchema from './findings.schema.json';
import { Mode, orbitsFields, tasks } from './catalog';

export const pluginId = 'semantic-series-workspace';

export interface Passage {
  path: string;
  sha256: string;
  start: number;
  end: number;
  firstLine: number;
  lastLine: number;
  quote: string;
}

export type Feedback = 'comment' | 'reply' | 'accept' | 'reject' | 'request-change';

export interface Draft {
  id: string;
  task: typeof tasks[number];
  source: Passage;
  provider: { id: string; model: string; endpoint: string };
  mode: Mode;
  createdAt: string;
  privacy: 'vault-local';
  state: 'dry-request';
  evidence: 'unreviewed';
  proposer: 'local-operator';
  sourceRecordId: null;
  editionId: null;
  receiptRefs: string[];
}

export interface SavedResult {
  draft: Draft;
  history: { id: string; action: Feedback; note: string; at: string; actor: 'local-operator'; replyTo?: string }[];
}

export async function sha256(bytes: ArrayBuffer | Uint8Array<ArrayBuffer>): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), byte => byte.toString(16).padStart(2, '0')).join('');
}

export function matchesPassage(source: Passage, text: string, hash: string): boolean {
  return source.sha256 === hash && text.slice(source.start, source.end) === source.quote;
}

export function requestEnvelope(draft: Draft) {
  return {
    schema: 'semantic-series.dry-request/1',
    producer: pluginId,
    producerVersion: '0.1.0',
    ...draft,
    permittedContext: [draft.source],
    localObservations: [{ check: 'sha256-and-exact-span', version: '1', sourceHash: draft.source.sha256 }],
    governingRules: [],
    rulingRefs: [],
    missingContext: ['Registered source identity and any supporting evidence or governing rules were not supplied.'],
    responseContract: {
      schema: draft.task.responseSchema,
      jsonSchema: {
        ...findingsSchema,
        properties: {
          ...findingsSchema.properties,
          sourceSha256: { const: draft.source.sha256 },
          recommendation: draft.task.taskClass === 'canon_assessment'
            ? findingsSchema.properties.recommendation : { enum: [null, 'cannot_assess'] }
        }
      },
      allowedSpan: { start: draft.source.start, end: draft.source.end, offsetUnit: 'UTF-16' },
      authority: 'proposals-only'
    },
    ...(draft.task.id.startsWith('orbits28_extract/') ? {
      orbits: orbitsFields.map(field => ({ field, applicability: 'unknown', value: null }))
    } : {})
  };
}
