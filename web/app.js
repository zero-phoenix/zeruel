const $ = id => document.getElementById(id);
let timer;
let session = 0; // Responses from a previous connection are ignored.
let idToken = ''; // Google ID token, kept only in memory for this tab.
const auth = () => idToken ? 'Google ' + idToken : 'Bearer ' + $('token').value;
async function request(path, body) {
  const mine = session;
  const response = await fetch(path, {method: body ? 'POST' : 'GET',
    headers: {'Authorization': auth(), 'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined, cache: 'no-store'});
  const data = await response.json();
  if (mine !== session) throw new Error('stale');
  show(data);
  if (!response.ok) throw new Error(data.state);
  return data;
}
function show(data) {
  $('report').textContent = JSON.stringify(data, null, 2);
  $('indicator').textContent = data.state === 'active' ? 'Activo · prueba sintética' :
    data.state === 'disconnected' ? 'Desconectado' :
    data.state === 'synthetic_success' ? 'Completado · prueba sintética' : 'Pausado · ' + data.state;
}
function fail() { clearTimeout(timer); $('indicator').textContent = 'Desconectado · no se confirmó la conexión'; }
const pendingAutorun = () => {
  const id = sessionStorage.getItem('zeruel_autorun') || '';
  return /^[a-f0-9]{32}$/.test(id) ? id : '';
};
async function connect(google = false) {
  try {
    await request('/api/status'); $('run').disabled = false; $('restore').disabled = false;
    const id = google && idToken && pendingAutorun();
    if (id) {
      // Consume once, even if the response is lost; the checkpoint can be queried by this id.
      sessionStorage.removeItem('zeruel_autorun');
      sessionStorage.removeItem('zeruel_autorun_retry');
      sessionStorage.removeItem('zeruel_hint');
      await runProbe(id);
    }
  }
  catch { fail(); }
}
$('connect').onclick = () => { idToken = ''; connect(); };
// Google sign-in by full-page redirect (OpenID Connect implicit id_token): no popups, FedCM or
// third-party scripts. state and nonce live only in this tab's sessionStorage.
const hex = n => [...crypto.getRandomValues(new Uint8Array(n))].map(b => b.toString(16).padStart(2, '0')).join('');
async function startGoogle(prompt = 'select_account') {
  const mine = session;
  try {
    const config = await (await fetch('/api/config', {cache: 'no-store'})).json();
    if (mine !== session) return;
    if (!config.google_client_id) return show({state: 'google_unavailable'});
    const flow = {state: hex(16), nonce: hex(16)};
    sessionStorage.setItem('zeruel_oidc', JSON.stringify(flow));
    location.assign('https://accounts.google.com/o/oauth2/v2/auth?' + new URLSearchParams({
      client_id: config.google_client_id, redirect_uri: location.origin + '/', response_type: 'id_token',
      scope: 'openid email', prompt, ...flow,
      // With several Google sessions open, prompt=none fails with «choose an account»
      // unless the account is hinted. The hint only travels in the autorun fragment.
      ...(sessionStorage.getItem('zeruel_hint') ? {login_hint: sessionStorage.getItem('zeruel_hint')} : {})}));
  } catch { show({state: 'google_unavailable'}); }
}
$('google').onclick = () => startGoogle();
async function finishGoogle() {
  if (!location.hash.includes('id_token=') && !location.hash.includes('error=')) return;
  const reply = new URLSearchParams(location.hash.slice(1));
  history.replaceState(null, '', location.pathname); // Removes the token from the address bar.
  let flow = {};
  try { flow = JSON.parse(sessionStorage.getItem('zeruel_oidc') || '{}'); } catch { /* invalid */ }
  sessionStorage.removeItem('zeruel_oidc');
  const token = reply.get('id_token');
  if (!flow.state || reply.get('state') !== flow.state) return show({state: 'google_state_mismatch'});
  if (!token) {
    const error = reply.get('error');
    if (pendingAutorun() && /^(interaction_required|login_required|consent_required)$/.test(error || '') &&
        !sessionStorage.getItem('zeruel_autorun_retry')) {
      sessionStorage.setItem('zeruel_autorun_retry', '1');
      return startGoogle('select_account');
    }
    return show({state: 'google_' + (error || 'cancelled')});
  }
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const claims = JSON.parse(atob(part + '='.repeat((4 - part.length % 4) % 4)));
    if (claims.nonce !== flow.nonce) return show({state: 'google_nonce_mismatch'});
  } catch { return show({state: 'google_invalid_token'}); }
  session++; idToken = token; await connect(true);
}
async function runProbe(id) {
  const mine = session;
  $('run').disabled = true;
  try {
    id = id || hex(16);
    $('task').value = id;
    const data = await request('/api/probe', {id});
    if (data.state === 'active') timer = setTimeout(poll, 2000);
    else $('run').disabled = false;
  } catch {
    if (mine !== session) return;
    // A lost response must never cause another inference. Recover by id instead.
    try {
      const data = await request('/api/checkpoint/' + id);
      if (data.state === 'active') timer = setTimeout(poll, 2000);
    } catch { /* Keep the id visible for manual checkpoint lookup. */ }
    if (mine === session) $('run').disabled = false;
  }
}
$('run').onclick = () => runProbe();
async function poll() {
  try {
    const data = await request('/api/status');
    if (data.state === 'active') timer = setTimeout(poll, 2000);
    else $('run').disabled = false;
  } catch { fail(); $('run').disabled = true; }
}
$('restore').onclick = async () => {
  if (!/^[a-f0-9]{32}$/.test($('task').value)) return show({state:'invalid_id'});
  try { await request('/api/checkpoint/' + $('task').value); } catch { /* displayed above */ }
};
$('disconnect').onclick = () => {
  session++; clearTimeout(timer); $('token').value = ''; idToken = ''; $('run').disabled = true; $('restore').disabled = true;
  sessionStorage.removeItem('zeruel_autorun'); sessionStorage.removeItem('zeruel_autorun_retry');
  sessionStorage.removeItem('zeruel_hint');
  show({state:'disconnected'});
};
const autorun = /^#autorun=([a-f0-9]{32})(?:&hint=([A-Za-z0-9._%+-]{1,64}(?:%40|@)[A-Za-z0-9.-]{1,180}\.[A-Za-z]{2,24}))?$/.exec(location.hash);
// A malformed %-sequence must not throw (URIError) nor redirect: such a fragment is invalid.
const hint = (() => {
  if (!autorun || !autorun[2]) return '';
  try {
    const d = decodeURIComponent(autorun[2]);
    return /^[^@\s%]{1,64}@[A-Za-z0-9.-]{1,180}\.[A-Za-z]{2,24}$/.test(d) ? d : null;
  } catch { return null; }
})();
if (autorun && hint !== null) {
  sessionStorage.setItem('zeruel_autorun', autorun[1]);
  if (hint) sessionStorage.setItem('zeruel_hint', hint);
  else sessionStorage.removeItem('zeruel_hint');
  sessionStorage.removeItem('zeruel_autorun_retry');
  history.replaceState(null, '', location.pathname);
  startGoogle('none');
} else {
  finishGoogle();
}
