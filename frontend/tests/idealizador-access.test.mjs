import assert from 'node:assert/strict';
import { test } from 'node:test';
import { authorizeIdealizador, hasIdealizadorAccess, clearIdealizadorAccess } from '../src/idealizadorAccess.ts';

const reply = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

function installSessionStorage() {
  const original = Object.getOwnPropertyDescriptor(globalThis, 'sessionStorage');
  const values = new Map();
  Object.defineProperty(globalThis, 'sessionStorage', {
    configurable: true,
    value: {
      getItem: key => values.get(key) ?? null,
      setItem: (key, value) => values.set(key, String(value)),
      removeItem: key => values.delete(key),
    },
  });
  return () => {
    if (original) Object.defineProperty(globalThis, 'sessionStorage', original);
    else delete globalThis.sessionStorage;
  };
}

test('idealizador access stores only an authorized session marker', async t => {
  const restoreStorage = installSessionStorage();
  const fetch = t.mock.method(globalThis, 'fetch', async (_url, init) => {
    assert.deepEqual(JSON.parse(init.body), { key: 'correct-key' });
    return reply(200, { data: { authorized: true } });
  });
  try {
    assert.equal(hasIdealizadorAccess(), false);
    await authorizeIdealizador('correct-key');
    assert.equal(hasIdealizadorAccess(), true);
    assert.match(fetch.mock.calls[0].arguments[0], /\/access\/idealizador$/);
    clearIdealizadorAccess();
    assert.equal(hasIdealizadorAccess(), false);
  } finally {
    restoreStorage();
    fetch.mock.restore();
  }
});

test('idealizador access propagates an invalid key without granting access', async t => {
  const restoreStorage = installSessionStorage();
  const fetch = t.mock.method(globalThis, 'fetch', async () => reply(401, {
    error: { code: 'IDEALIZADOR_ACCESS_DENIED', message: 'Palavra-chave incorreta.' },
  }));
  try {
    await assert.rejects(authorizeIdealizador('wrong-key'), error => error.status === 401 && error.code === 'IDEALIZADOR_ACCESS_DENIED');
    assert.equal(hasIdealizadorAccess(), false);
  } finally {
    restoreStorage();
    fetch.mock.restore();
  }
});
