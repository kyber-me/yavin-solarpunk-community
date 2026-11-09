import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createConversation, listAgents, sendMessage, listConversations, listMessages, updateConversationTitle, ChatApiError } from '../src/chatApi.ts';
import { discardLocalHistory } from '../src/conversations.ts';

const info = { conversation_id: 'Conv_server', participant_id: 'opaque-agent', created_at: '2026-11-07T12:00:00Z', title: 'Conversa com Íris' };
const reply = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

test('catalog uses opaque IDs, validates payload and propagates API errors', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { agents: [{ id: 'opaque-agent', name: 'Íris', public_description: null }] } }));
  assert.deepEqual(await listAgents(), [{ id: 'opaque-agent', name: 'Íris', public_description: null }]);
  assert.match(fetch.mock.calls[0].arguments[0], /\/agents$/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { agents: [{ id: 'opaque-agent', name: 'Íris', public_description: 'Investiga energia em Yavin.' }] } }));
  assert.equal((await listAgents())[0].public_description, 'Investiga energia em Yavin.');
  fetch.mock.mockImplementation(async () => reply(200, { data: { agents: [{ id: 'opaque-agent', name: 'Íris' }] } }));
  await assert.rejects(listAgents(), /catálogo/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { agents: [{ id: 'x' }] } }));
  await assert.rejects(listAgents(), /catálogo/);
  fetch.mock.mockImplementation(async () => reply(503, { error: { message: 'Indisponível' } }));
  await assert.rejects(listAgents(), /Indisponível/);
  fetch.mock.restore();
});

test('creation confirms server metadata and sends owner and conversation details', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(201, { data: info }));
  assert.deepEqual(await createConversation('opaque-agent', 'Conversa com Íris'), { existing: false, conversation: info });
  assert.match(fetch.mock.calls[0].arguments[0], /\/conversation\/create$/);
  assert.deepEqual(JSON.parse(fetch.mock.calls[0].arguments[1].body), {
    owner_id: 'idealizador', conversation_details: { title: 'Conversa com Íris', participant_id: 'opaque-agent' },
  });
  fetch.mock.mockImplementation(async () => reply(201, { data: { ...info, participant_id: 'wrong' } }));
  await assert.rejects(createConversation('opaque-agent', 'Conversa com Íris'), /outro participante/);
  fetch.mock.mockImplementation(async () => reply(201, { data: { ...info, conversation_id: '' } }));
  await assert.rejects(createConversation('opaque-agent', 'Conversa com Íris'), /conversa válida/);
  fetch.mock.restore();
});

test('only the agreed 409 code is offered as an existing conversation', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(409, {
    error: { code: 'CONVERSATION_ALREADY_ACTIVE', details: info },
  }));
  assert.deepEqual(await createConversation('opaque-agent', 'Conversa com Íris'), { existing: true, conversation: info });
  fetch.mock.mockImplementation(async () => reply(409, { error: { code: 'OTHER_CONFLICT', message: 'Outro conflito' } }));
  await assert.rejects(createConversation('opaque-agent', 'Conversa com Íris'), error => error instanceof ChatApiError && error.code === 'OTHER_CONFLICT');
  fetch.mock.restore();
});

test('renaming sends owner and returns the persisted title', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { conversation_id: 'Conv_server', title: 'Energia solar' } }));
  assert.equal(await updateConversationTitle('Conv_server', 'Energia solar'), 'Energia solar');
  assert.match(fetch.mock.calls[0].arguments[0], /\/conversations\/Conv_server\/title$/);
  assert.equal(fetch.mock.calls[0].arguments[1].method, 'PATCH');
  assert.deepEqual(JSON.parse(fetch.mock.calls[0].arguments[1].body), { owner_id: 'idealizador', title: 'Energia solar' });
  fetch.mock.mockImplementation(async () => reply(403, { error: { code: 'CONVERSATION_FORBIDDEN', message: 'Sem acesso' } }));
  await assert.rejects(updateConversationTitle('Conv_server', 'Outro'), error => error instanceof ChatApiError && error.status === 403);
  fetch.mock.restore();
});

test('chat uses conversation ID, never local thread ID, and preserves server errors', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { content: 'Resposta' } }));
  assert.equal(await sendMessage('Conv_server', 'Olá'), 'Resposta');
  assert.match(fetch.mock.calls[0].arguments[0], /\/conversation\/message$/);
  assert.deepEqual(JSON.parse(fetch.mock.calls[0].arguments[1].body), { conversation_id: 'Conv_server', sender_id: 'idealizador', message: 'Olá' });
  fetch.mock.mockImplementation(async () => reply(404, { error: { message: 'Conversa ausente' } }));
  await assert.rejects(sendMessage('Conv_server', 'Olá'), error => error.status === 404 && error.message === 'Conversa ausente');
  fetch.mock.restore();
});

test('network failures are explicit and invalid answers are rejected', async t => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => { throw new TypeError('offline'); });
  await assert.rejects(createConversation('opaque-agent', 'Conversa com Íris'), /acessar a API/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { content: '' } }));
  await assert.rejects(sendMessage('Conv_server', 'Olá'), /vazia ou inválida/);
  fetch.mock.restore();
});

test('legacy local history is removed without reading or importing it', () => {
  const removed = [];
  const original = Object.getOwnPropertyDescriptor(globalThis, 'localStorage');
  Object.defineProperty(globalThis, 'localStorage', { configurable: true, value: {
    getItem() { throw new Error('Legacy records must never be read'); },
    setItem() { throw new Error('History must never be stored locally'); },
    removeItem(key) { removed.push(key); },
  } });
  try { discardLocalHistory(); assert.deepEqual(removed, ['yavin.conversations.v1']); }
  finally {
    if (original) Object.defineProperty(globalThis, 'localStorage', original);
    else delete globalThis.localStorage;
  }
});

test('conversation history uses persisted records and follows server pagination', async t => {
  const record = { ...info, participant_name: 'Silas', active: true };
  const fetch = t.mock.method(globalThis, 'fetch', async url => {
    const offset = new URL(url).searchParams.get('offset');
    return reply(200, { data: { conversations: offset === '0' ? [record] : [], next_offset: offset === '0' ? 100 : null } });
  });
  assert.deepEqual(await listConversations(), [record]);
  assert.equal(fetch.mock.calls.length, 2);
  assert.match(fetch.mock.calls[0].arguments[0], /\/conversations\?sender_id=idealizador/);
  fetch.mock.mockImplementation(async () => reply(503, { error: { message: 'Banco indisponível' } }));
  await assert.rejects(listConversations(), /Banco indisponível/);
  fetch.mock.restore();
});

test('messages use server IDs and dates and reject malformed or inaccessible history', async t => {
  const message = { id: 'server-message', sender_id: 'silas', content: 'Persistida', created_at: info.created_at };
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(200, { data: { messages: [message], next_offset: null } }));
  assert.deepEqual(await listMessages('server-id'), [message]);
  assert.match(fetch.mock.calls[0].arguments[0], /\/conversations\/server-id\/messages\?/);
  fetch.mock.mockImplementation(async () => reply(200, { data: { messages: [{ ...message, created_at: 'invalid' }], next_offset: null } }));
  await assert.rejects(listMessages('server-id'), /mensagem inválida/);
  fetch.mock.mockImplementation(async () => reply(403, { error: { message: 'Sem acesso' } }));
  await assert.rejects(listMessages('server-id'), error => error.status === 403);
  fetch.mock.restore();
});
