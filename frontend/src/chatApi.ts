export type AgentOption = { id: string; name: string };
export type ConversationMetadata = { conversation_id: string; participant_id: string; created_at: string };
export type CreationResult = { existing: boolean; conversation: ConversationMetadata };

const API_URL = import.meta.env?.VITE_API_URL ?? 'http://127.0.0.1:8000';
export const SENDER_ID = 'idealizador';

export class ChatApiError extends Error {
  status: number;
  code?: string;
  constructor(message: string, status: number, code?: string) {
    super(message); this.status = status; this.code = code;
  }
}

function object(value: unknown): Record<string, unknown> | undefined {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown> : undefined;
}

function metadata(value: unknown): ConversationMetadata {
  const item = object(value);
  if (!item || typeof item.conversation_id !== 'string' || !item.conversation_id.trim()
    || typeof item.participant_id !== 'string' || !item.participant_id.trim()
    || typeof item.created_at !== 'string' || !Number.isFinite(Date.parse(item.created_at))) {
    throw new Error('A API não retornou uma conversa válida. Tente iniciar a conversa novamente.');
  }
  return item as ConversationMetadata;
}

async function request(path: string, init: RequestInit = {}) {
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...init, signal: init.signal ?? AbortSignal.timeout(30000),
    });
  } catch {
    throw new Error('Não foi possível acessar a API. Verifique a conexão e tente novamente.');
  }
  const payload: unknown = await response.json().catch(() => null);
  const envelope = object(payload);
  const error = object(envelope?.error);
  return { response, data: envelope?.data, error };
}

function fail(status: number, error: Record<string, unknown> | undefined, fallback: string): never {
  throw new ChatApiError(typeof error?.message === 'string' ? error.message : fallback,
    status, typeof error?.code === 'string' ? error.code : undefined);
}

export async function listAgents(signal?: AbortSignal): Promise<AgentOption[]> {
  const { response, data, error } = await request('/agents', { signal, cache: 'no-store' });
  if (!response.ok || error) fail(response.status, error, 'Não foi possível carregar os agentes.');
  const agents = object(data)?.agents;
  if (!Array.isArray(agents) || !agents.every(item => {
    const agent = object(item);
    return agent && typeof agent.id === 'string' && !!agent.id.trim()
      && typeof agent.name === 'string' && !!agent.name.trim();
  })) throw new Error('A API não retornou um catálogo de agentes válido.');
  const typed = agents as AgentOption[];
  if (new Set(typed.map(agent => agent.id)).size !== typed.length) {
    throw new Error('O catálogo retornou agentes com IDs repetidos.');
  }
  return typed;
}

export async function createConversation(participantId: string): Promise<CreationResult> {
  const { response, data, error } = await request('/create-conversation', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sender_id: SENDER_ID, participant_id: participantId }),
  });
  const existing = response.status === 409 && error?.code === 'CONVERSATION_ALREADY_ACTIVE';
  if (!existing && (response.status !== 201 || error)) {
    fail(response.status, error, 'Não foi possível iniciar a conversa.');
  }
  const conversation = metadata(existing ? error?.details : data);
  if (conversation.participant_id !== participantId) {
    throw new Error('A API retornou uma conversa com outro participante. Tente novamente.');
  }
  return { existing, conversation };
}

export async function sendMessage(conversationId: string, content: string): Promise<string> {
  const { response, data, error } = await request('/chat', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, sender_id: SENDER_ID, message: content }),
    signal: AbortSignal.timeout(120000),
  });
  if (!response.ok || error) fail(response.status, error, 'Não foi possível enviar a mensagem.');
  const answer = object(data)?.content;
  if (typeof answer !== 'string' || !answer.trim()) throw new Error('O agente retornou uma resposta vazia ou inválida.');
  return answer;
}
