const $ = id => document.getElementById(id);
let timer;
async function request(path, body) {
  const response = await fetch(path, {method: body ? 'POST' : 'GET',
    headers: {'Authorization': 'Bearer ' + $('token').value, 'Content-Type': 'application/json'},
    body: body ? JSON.stringify(body) : undefined, cache: 'no-store'});
  const data = await response.json();
  show(data);
  if (!response.ok) throw new Error(data.state);
  return data;
}
function show(data) {
  $('report').textContent = JSON.stringify(data, null, 2);
  $('indicator').textContent = data.state === 'active' ? 'Activo · prueba sintética' :
    data.state === 'disconnected' ? 'Desconectado' : 'Pausado · ' + data.state;
}
function fail() { clearTimeout(timer); $('indicator').textContent = 'Desconectado · no se confirmó la conexión'; }
$('connect').onclick = async () => {
  try { await request('/api/status'); $('run').disabled = false; $('restore').disabled = false; }
  catch { fail(); }
};
$('run').onclick = async () => {
  $('run').disabled = true;
  const id = crypto.randomUUID().replaceAll('-', ''); $('task').value = id;
  try {
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
  clearTimeout(timer); $('token').value = ''; $('run').disabled = true; $('restore').disabled = true;
  show({state:'disconnected'});
};
