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
async function connect() {
  try { await request('/api/status'); $('run').disabled = false; $('restore').disabled = false; }
  catch { fail(); }
}
$('connect').onclick = () => { idToken = ''; connect(); };
// Google sign-in by full-page redirect (OpenID Connect implicit id_token): no popups, FedCM or
// third-party scripts. state and nonce live only in this tab's sessionStorage.
const hex = n => [...crypto.getRandomValues(new Uint8Array(n))].map(b => b.toString(16).padStart(2, '0')).join('');
$('google').onclick = async () => {
  try {
    const config = await (await fetch('/api/config', {cache: 'no-store'})).json();
    if (!config.google_client_id) return show({state: 'google_unavailable'});
    const flow = {state: hex(16), nonce: hex(16)};
    sessionStorage.setItem('zeruel_oidc', JSON.stringify(flow));
    location.assign('https://accounts.google.com/o/oauth2/v2/auth?' + new URLSearchParams({
      client_id: config.google_client_id, redirect_uri: location.origin + '/', response_type: 'id_token',
      scope: 'openid email', prompt: 'select_account', ...flow}));
  } catch { show({state: 'google_unavailable'}); }
};
function finishGoogle() {
  if (!location.hash.includes('id_token=') && !location.hash.includes('error=')) return;
  const reply = new URLSearchParams(location.hash.slice(1));
  history.replaceState(null, '', location.pathname); // Removes the token from the address bar.
  let flow = {};
  try { flow = JSON.parse(sessionStorage.getItem('zeruel_oidc') || '{}'); } catch { /* invalid */ }
  sessionStorage.removeItem('zeruel_oidc');
  const token = reply.get('id_token');
  if (!token) return show({state: 'google_' + (reply.get('error') || 'cancelled')});
  if (!flow.state || reply.get('state') !== flow.state) return show({state: 'google_state_mismatch'});
  try {
    const part = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const claims = JSON.parse(atob(part + '='.repeat((4 - part.length % 4) % 4)));
    if (claims.nonce !== flow.nonce) return show({state: 'google_nonce_mismatch'});
  } catch { return show({state: 'google_invalid_token'}); }
  session++; idToken = token; connect();
}
finishGoogle();
$('run').onclick = async () => {
  $('run').disabled = true;
  try {
    const id = [...crypto.getRandomValues(new Uint8Array(16))].map(b => b.toString(16).padStart(2, '0')).join('');
    $('task').value = id;
    const data = await request('/api/probe', {id});
    if (data.state === 'active') timer = setTimeout(poll, 2000);
    else $('run').disabled = false;
  } catch { $('run').disabled = false; }
};
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
  show({state:'disconnected'});
};
