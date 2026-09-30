const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const {webcrypto} = require('node:crypto');
const vm = require('node:vm');

// SIMULADA: DOM, Google callbacks and server responses. No real credentials or network.
const source = readFileSync(require('node:path').join(__dirname, '../web/app.js'), 'utf8');
const id = '1234567890abcdef1234567890abcdef';
const tick = () => new Promise(resolve => setImmediate(resolve));
function page({hash = '', storage = new Map(), respond} = {}) {
  const elements = Object.fromEntries(['token', 'task', 'report', 'indicator', 'connect',
    'google', 'run', 'restore', 'disconnect'].map(key => [key, {value: '', textContent: '', disabled: true}]));
  const calls = [], redirects = [], timers = [];
  const location = {hash, origin: 'https://zeruel.example', pathname: '/', assign: url => redirects.push(url)};
  const context = vm.createContext({
    document: {getElementById: key => elements[key]}, location,
    history: {replaceState: () => { location.hash = ''; }}, crypto: webcrypto, URLSearchParams,
    sessionStorage: {
      getItem: key => storage.get(key) ?? null,
      setItem: (key, value) => storage.set(key, String(value)), removeItem: key => storage.delete(key),
    },
    atob: value => Buffer.from(value, 'base64').toString('binary'),
    setTimeout: fn => { timers.push(fn); return timers.length; }, clearTimeout: () => {},
    fetch: async (path, options) => {
      calls.push({path, options});
      const result = respond ? await respond(path, options) : null;
      return result || {ok: true, json: async () => path === '/api/config'
        ? {google_client_id: 'synthetic-client'} : {state: path === '/api/probe' ? 'active' : 'paused'}};
    },
  });
  vm.runInContext(source, context);
  return {context, elements, calls, redirects, storage, location, timers};
}
function callback(storage, {error, state, nonce} = {}) {
  const flow = JSON.parse(storage.get('zeruel_oidc'));
  const params = new URLSearchParams({state: state || flow.state});
  if (error) params.set('error', error);
  else params.set('id_token', 'synthetic.' + Buffer.from(JSON.stringify({nonce: nonce || flow.nonce}))
    .toString('base64url') + '.signature');
  return '#' + params;
}
async function begin() {
  const p = page({hash: '#autorun=' + id});
  await tick();
  return p;
}

test('strict autorun captures id, removes hash and starts Google with prompt=none', async () => {
  const p = await begin();
  assert.equal(p.storage.get('zeruel_autorun'), id);
  assert.equal(p.location.hash, '');
  const url = new URL(p.redirects[0]);
  assert.equal(url.searchParams.get('prompt'), 'none');
  assert.equal(url.searchParams.get('response_type'), 'id_token');
  assert.equal(url.searchParams.get('scope'), 'openid email');
  assert.ok(url.searchParams.get('state'));
  assert.ok(url.searchParams.get('nonce'));
  assert.equal(p.calls.some(call => call.path === '/api/probe'), false);
});

test('invalid autorun fragments never redirect or submit', async () => {
  for (const hash of ['#autorun=' + id.toUpperCase(), '#autorun=' + id + '&extra=1',
    '#autorun=' + id.slice(1), '#autorun=' + id + '0', '#autorun=arbitrary']) {
    const p = page({hash});
    await tick();
    assert.equal(p.calls.length, 0);
    assert.equal(p.storage.size, 0);
    assert.equal(p.redirects.length, 0);
  }
});

for (const error of ['interaction_required', 'login_required', 'consent_required']) {
  test(error + ' retries once with select_account across reloads', async () => {
    const p = await begin();
    const retry = page({storage: p.storage, hash: callback(p.storage, {error})});
    await tick();
    assert.equal(new URL(retry.redirects[0]).searchParams.get('prompt'), 'select_account');
    assert.equal(p.storage.get('zeruel_autorun_retry'), '1');
    const stopped = page({storage: p.storage, hash: callback(p.storage, {error})});
    await tick();
    assert.equal(stopped.redirects.length, 0);
    assert.equal(stopped.calls.length, 0);
    assert.equal(JSON.parse(stopped.elements.report.textContent).state, 'google_' + error);
  });
}

test('unsolicited error callback cannot trigger a retry', async () => {
  const p = await begin();
  const reply = page({storage: p.storage,
    hash: callback(p.storage, {error: 'interaction_required', state: 'wrong-state'})});
  await tick();
  assert.equal(reply.redirects.length, 0);
  assert.equal(reply.calls.length, 0);
  assert.equal(JSON.parse(reply.elements.report.textContent).state, 'google_state_mismatch');
});

test('access_denied does not retry', async () => {
  const p = await begin();
  const reply = page({storage: p.storage, hash: callback(p.storage, {error: 'access_denied'})});
  await tick();
  assert.equal(reply.redirects.length, 0);
  assert.equal(reply.calls.length, 0);
});

test('successful Google callback validates with server then submits only the scheduled id and polls', async () => {
  const p = await begin();
  p.storage.set('zeruel_autorun_retry', '1');
  const reply = page({storage: p.storage, hash: callback(p.storage)});
  await tick();
  assert.deepEqual(reply.calls.map(call => call.path), ['/api/status', '/api/probe']);
  assert.deepEqual(JSON.parse(reply.calls[1].options.body), {id});
  assert.match(reply.calls[1].options.headers.Authorization, /^Google /);
  assert.equal(reply.elements.task.value, id);
  assert.equal(reply.location.hash, '');
  assert.equal(reply.storage.size, 0); // No token, pending id or retry marker stored.
  assert.equal(reply.timers.length, 1);
  await reply.timers[0]();
  assert.equal(reply.calls.at(-1).path, '/api/status');
  assert.equal(reply.elements.run.disabled, false);
  const reload = page({storage: reply.storage});
  await tick();
  assert.equal(reload.calls.length, 0);
});

test('wrong state or nonce blocks authentication and autorun', async () => {
  for (const options of [{state: 'wrong-state'}, {nonce: 'wrong-nonce'}]) {
    const p = await begin();
    const reply = page({storage: p.storage, hash: callback(p.storage, options)});
    await tick();
    assert.equal(reply.calls.length, 0);
    assert.equal(reply.elements.run.disabled, true);
  }
});

test('server rejection of Google identity never submits a task', async () => {
  const p = await begin();
  const reply = page({storage: p.storage, hash: callback(p.storage),
    respond: async () => ({ok: false, json: async () => ({state: 'unauthorized'})})});
  await tick();
  assert.deepEqual(reply.calls.map(call => call.path), ['/api/status']);
  assert.equal(reply.elements.run.disabled, true);
  assert.equal(reply.storage.get('zeruel_autorun'), id);
});

test('legacy bearer connection cannot consume pending autorun', async () => {
  const storage = new Map([['zeruel_autorun', id]]);
  const p = page({storage});
  p.elements.token.value = 'synthetic-legacy-token';
  p.elements.connect.onclick();
  await tick();
  assert.deepEqual(p.calls.map(call => call.path), ['/api/status']);
  assert.equal(storage.get('zeruel_autorun'), id);
});

test('disconnect before server verification finishes prevents submission', async () => {
  const p = await begin();
  let complete;
  const reply = page({storage: p.storage, hash: callback(p.storage),
    respond: () => new Promise(resolve => { complete = resolve; })});
  reply.elements.disconnect.onclick();
  complete({ok: true, json: async () => ({state: 'paused'})});
  await tick();
  assert.deepEqual(reply.calls.map(call => call.path), ['/api/status']);
  assert.equal(reply.elements.run.disabled, true);
  assert.equal(reply.storage.size, 0);
});

test('lost probe response consumes autorun without an automatic resubmission', async () => {
  const p = await begin();
  const reply = page({storage: p.storage, hash: callback(p.storage), respond: async path => {
    if (path === '/api/probe') throw new Error('network');
  }});
  await tick();
  assert.equal(reply.calls.filter(call => call.path === '/api/probe').length, 1);
  assert.equal(reply.storage.size, 0);
  assert.equal(reply.elements.task.value, id);
  assert.equal(reply.timers.length, 0);
});

test('manual Google sign-in still uses account selection and no autorun', async () => {
  const p = page();
  await p.elements.google.onclick();
  assert.equal(new URL(p.redirects[0]).searchParams.get('prompt'), 'select_account');
  const reply = page({storage: p.storage, hash: callback(p.storage)});
  await tick();
  assert.deepEqual(reply.calls.map(call => call.path), ['/api/status']);
  assert.equal(reply.elements.run.disabled, false);
});

test('new explicit autorun resets the retry marker and replaces the pending id', async () => {
  const storage = new Map([['zeruel_autorun_retry', '1'], ['zeruel_autorun', 'a'.repeat(32)]]);
  const p = page({hash: '#autorun=' + id, storage});
  await tick();
  assert.equal(storage.get('zeruel_autorun'), id);
  assert.equal(storage.has('zeruel_autorun_retry'), false);
  assert.equal(new URL(p.redirects[0]).searchParams.get('prompt'), 'none');
});

test('disconnect while loading Google configuration cancels the redirect', async () => {
  let complete;
  const p = page({hash: '#autorun=' + id,
    respond: () => new Promise(resolve => { complete = resolve; })});
  p.elements.disconnect.onclick();
  complete({ok: true, json: async () => ({google_client_id: 'synthetic-client'})});
  await tick();
  assert.equal(p.redirects.length, 0);
  assert.equal(p.storage.size, 0);
});

test('disconnect with probe in flight never re-enables run on the stale response', async () => {
  const p = await begin();
  let complete;
  const reply = page({storage: p.storage, hash: callback(p.storage), respond: path => {
    if (path === '/api/probe') return new Promise(resolve => { complete = resolve; });
  }});
  await tick();
  reply.elements.disconnect.onclick();
  complete({ok: true, json: async () => ({state: 'active'})});
  await tick();
  assert.equal(reply.elements.run.disabled, true);
  assert.equal(reply.timers.length, 0);
  assert.equal(reply.storage.size, 0);
});
