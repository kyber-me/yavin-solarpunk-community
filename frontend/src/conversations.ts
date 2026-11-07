export type Mode = 'conversation' | 'meeting';
export type Message = { id: string; author: string; content: string; createdAt: string; kind?: 'user' | 'agent' | 'system' };
export type Conversation = {
  id: string;
  mode: Mode;
  serverConversationId?: string;
  participantId?: string;
  resumed?: boolean;
  unavailableReason?: string;
  title: string;
  participants: string[];
  messages: Message[];
  draft: string;
  createdAt: string;
};

export const STORAGE_KEY = 'yavin.conversations.v1';

export function newConversation(mode: Mode, title: string, participants: string[]): Conversation {
  return { id: crypto.randomUUID(), mode, title, participants, messages: [], draft: '', createdAt: new Date().toISOString() };
}

export function initialConversations(): Conversation[] {
  return [];
}

function isConversation(value: unknown): value is Conversation {
  if (!value || typeof value !== 'object') return false;
  const item = value as Record<string, unknown>;
  return typeof item.id === 'string' && typeof item.title === 'string' && typeof item.draft === 'string'
    && typeof item.createdAt === 'string' && Number.isFinite(Date.parse(item.createdAt))
    && (item.mode === 'conversation' || item.mode === 'meeting')
    && (item.serverConversationId === undefined || (typeof item.serverConversationId === 'string' && !!item.serverConversationId.trim()))
    && (item.participantId === undefined || (typeof item.participantId === 'string' && !!item.participantId.trim()))
    && (item.serverConversationId === undefined || (item.mode === 'conversation' && typeof item.participantId === 'string'))
    && (item.resumed === undefined || typeof item.resumed === 'boolean')
    && (item.unavailableReason === undefined || typeof item.unavailableReason === 'string')
    && Array.isArray(item.participants) && item.participants.every(p => typeof p === 'string')
    && Array.isArray(item.messages) && item.messages.every(message =>
      message && typeof message.id === 'string' && typeof message.author === 'string'
      && typeof message.content === 'string' && typeof message.createdAt === 'string'
      && Number.isFinite(Date.parse(message.createdAt))
      && (message.kind === undefined || ['user', 'agent', 'system'].includes(message.kind)));
}

export function readConversations(): { conversations: Conversation[]; warning: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { conversations: initialConversations(), warning: '' };
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed) || !parsed.every(isConversation)) throw new Error('Invalid history');
    return { conversations: parsed.length ? parsed : initialConversations(), warning: '' };
  } catch {
    return { conversations: initialConversations(), warning: 'O histórico local não pôde ser recuperado. Suas novas conversas continuam disponíveis nesta sessão.' };
  }
}
