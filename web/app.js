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
async function initGoogle() {
  try {
    const config = await (await fetch('/api/config', {cache: 'no-store'})).json();
    if (!config.google_client_id) return;
    const ready = () => window.google && google.accounts && google.accounts.id;
    for (let i = 0; i < 50 && !ready(); i++) await new Promise(r => setTimeout(r, 100));
    if (!ready()) return;
    google.accounts.id.initialize({client_id: config.google_client_id, auto_select: true,
      callback: r => { session++; idToken = r.credential; connect(); }});
    google.accounts.id.renderButton($('google'), {theme: 'filled_blue', size: 'large', text: 'signin_with', locale: 'es'});
  } catch { /* The private key remains available. */ }
}
initGoogle();
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
  if (window.google && google.accounts && google.accounts.id) google.accounts.id.disableAutoSelect();
  show({state:'disconnected'});
};
