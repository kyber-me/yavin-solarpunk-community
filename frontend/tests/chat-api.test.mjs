import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createConversation, listAgents, sendMessage, ChatApiError } from '../src/chatApi.ts';
import { readConversations, STORAGE_KEY } from '../src/conversations.ts';

const info = { conversation_id: 'Conv_server', participant_id: 'opaque-agent', created_at: '2026-11-07T12:00:00Z' };
const reply = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

test('catalog uses opaque IDs, validates payload and propagates API errors', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { agents: [{ id: 'opaque-agent', name: 'Íris' }] } }));
  assert.deepEqual(await listAgents(), [{ id: 'opaque-agent', name: 'Íris' }]);
  assert.match(fetch.mock.calls[0].arguments[0], /\/agents$/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { agents: [{ id: 'x' }] } }));
  await assert.rejects(listAgents(), /catálogo/);
  fetch.mock.mockImplementation(async () => reply(503, { error: { message: 'Indisponível' } }));
  await assert.rejects(listAgents(), /Indisponível/);
  fetch.mock.restore();
});

test('creation confirms server metadata and sends only sender and selected participant', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(201, { data: info }));
  assert.deepEqual(await createConversation('opaque-agent'), { existing: false, conversation: info });
  assert.deepEqual(JSON.parse(fetch.mock.calls[0].arguments[1].body), { sender_id: 'idealizador', participant_id: 'opaque-agent' });
  fetch.mock.mockImplementation(async () => reply(201, { data: { ...info, participant_id: 'wrong' } }));
  await assert.rejects(createConversation('opaque-agent'), /outro participante/);
  fetch.mock.mockImplementation(async () => reply(201, { data: { ...info, conversation_id: '' } }));
  await assert.rejects(createConversation('opaque-agent'), /conversa válida/);
  fetch.mock.restore();
});

test('only the agreed 409 code is offered as an existing conversation', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(409, {
    error: { code: 'CONVERSATION_ALREADY_ACTIVE', details: info },
  }));
  assert.deepEqual(await createConversation('opaque-agent'), { existing: true, conversation: info });
  fetch.mock.mockImplementation(async () => reply(409, { error: { code: 'OTHER_CONFLICT', message: 'Outro conflito' } }));
  await assert.rejects(createConversation('opaque-agent'), error => error instanceof ChatApiError && error.code === 'OTHER_CONFLICT');
  fetch.mock.restore();
});

test('chat uses conversation ID, never local thread ID, and preserves server errors', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { content: 'Resposta' } }));
  assert.equal(await sendMessage('Conv_server', 'Olá'), 'Resposta');
  assert.deepEqual(JSON.parse(fetch.mock.calls[0].arguments[1].body), { conversation_id: 'Conv_server', sender_id: 'idealizador', message: 'Olá' });
  fetch.mock.mockImplementation(async () => reply(404, { error: { message: 'Conversa ausente' } }));
  await assert.rejects(sendMessage('Conv_server', 'Olá'), error => error.status === 404 && error.message === 'Conversa ausente');
  fetch.mock.restore();
});

test('network failures are explicit and invalid answers are rejected', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('offline'); });
  await assert.rejects(createConversation('opaque-agent'), /acessar a API/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { content: '' } }));
  await assert.rejects(sendMessage('Conv_server', 'Olá'), /vazia ou inválida/);
  fetch.mock.restore();
});

test('legacy messages and drafts survive; a fresh browser has no fake conversation', () => {
  const legacy = [{ id: 'old-local', mode: 'conversation', title: 'Anterior', participants: ['Silas'], messages: [{ id: 'm1', author: 'Você', content: 'Histórico', createdAt: info.created_at }], draft: 'Rascunho', createdAt: info.created_at }];
  const storage = { getItem: key => key === STORAGE_KEY ? JSON.stringify(legacy) : null };
  const original = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: storage });
  try {
  assert.deepEqual(readConversations().conversations, legacy);
  assert.equal(readConversations().conversations[0].serverConversationId, undefined);
  storage.getItem = () => null;
  assert.deepEqual(readConversations().conversations, []);
  } finally {
    if (original) Object.defineProperty(globalThis, 'localStorage', original);
    else delete globalThis.localStorage;
  }
});
