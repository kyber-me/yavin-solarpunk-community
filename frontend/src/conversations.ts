export type Mode = 'conversation' | 'meeting';
export type Message = { id: string; author: string; content: string; createdAt: string; kind?: 'user' | 'agent' | 'system' };
export type Conversation = {
  id: string;
  mode: Mode;
  serverConversationId: string;
  participantId: string;
  unavailableReason?: string;
  title: string;
  participants: string[];
  messages: Message[];
  draft: string;
  createdAt: string;
};

// Remove only Yavin's retired local history; never read or import its records.
export function discardLocalHistory(): void {
  try { localStorage.removeItem('yavin.conversations.v1'); } catch { /* History always comes from the API. */ }
}
