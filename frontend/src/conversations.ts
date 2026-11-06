export type Mode = 'conversation' | 'meeting';
export type Message = { id: string; author: string; content: string; createdAt: string };
export type Conversation = {
  id: string;
  mode: Mode;
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
  return [newConversation('conversation', 'Primeira conversa', ['Silas'])];
}

function isConversation(value: unknown): value is Conversation {
  if (!value || typeof value !== 'object') return false;
  const item = value as Record<string, unknown>;
  return typeof item.id === 'string' && typeof item.title === 'string' && typeof item.draft === 'string'
    && typeof item.createdAt === 'string' && Number.isFinite(Date.parse(item.createdAt))
    && (item.mode === 'conversation' || item.mode === 'meeting')
    && Array.isArray(item.participants) && item.participants.every(p => typeof p === 'string')
    && Array.isArray(item.messages) && item.messages.every(message =>
      message && typeof message.id === 'string' && typeof message.author === 'string'
      && typeof message.content === 'string' && typeof message.createdAt === 'string'
      && Number.isFinite(Date.parse(message.createdAt)));
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
