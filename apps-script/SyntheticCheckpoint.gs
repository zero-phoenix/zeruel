/* Milestone-only storage. No Drive/Gmail scopes, documents or credentials. */
// Public web requests are deliberately disabled, including signed requests.
function doPost(e) {
  return ContentService.createTextOutput(JSON.stringify({ok:false}))
    .setMimeType(ContentService.MimeType.JSON);
}

// Deploy only as an API executable with access restricted to the owner.
function runCheckpoint(envelope) {
  try {
    const owner = PropertiesService.getScriptProperties().getProperty('ZERUEL_OWNER_EMAIL');
    const identity = Session.getEffectiveUser().getEmail();
    if (!owner || !identity || identity.toLowerCase() !== owner.toLowerCase()) return {ok:false};
    return processCheckpoint_({postData:{contents:JSON.stringify(envelope)}});
  } catch (_) {return {ok:false};}
}

function processCheckpoint_(e) {
  const reply = value => value;
  try {
    if (!e || !e.postData || e.postData.contents.length > 5000) return reply({ok:false});
    const body = JSON.parse(e.postData.contents);
    const props = PropertiesService.getScriptProperties();
    const secret = props.getProperty('ZERUEL_CHECKPOINT_SECRET');
    if (!secret || secret.length < 32 || typeof body.payload !== 'string' ||
        !/^[a-f0-9]{32}$/.test(body.nonce) ||
        !/^\d{10}$/.test(body.timestamp) || Math.abs(Date.now()/1000 - Number(body.timestamp)) > 120)
      return reply({ok:false});
    const message = body.timestamp + '\n' + body.nonce + '\n' + body.payload;
    const bytes = Utilities.computeHmacSha256Signature(message, secret, Utilities.Charset.UTF_8);
    const expected = bytes.map(b => ('0' + ((b+256)%256).toString(16)).slice(-2)).join('');
    if (typeof body.signature !== 'string' || body.signature.length !== expected.length)
      return reply({ok:false});
    let mismatch = 0;
    for (let i=0;i<expected.length;i++) mismatch |= expected.charCodeAt(i)^body.signature.charCodeAt(i);
    if (mismatch) return reply({ok:false});
    const data = JSON.parse(body.payload);
    if (!/^[a-f0-9]{32}$/.test(data.id) || !['get','claim','complete'].includes(data.action))
      return reply({ok:false});
    const lock = LockService.getScriptLock();
    if (!lock.tryLock(5000)) return reply({ok:false});
    try {
      const now = Math.floor(Date.now()/1000);
      const nonces = JSON.parse(props.getProperty('zeruel_nonces') || '{}');
      if (nonces[body.nonce]) return reply({ok:false});
      for (const key of Object.keys(nonces)) if (nonces[key] < now-120) delete nonces[key];
      if (Object.keys(nonces).length >= 60) return reply({ok:false});
      nonces[body.nonce] = now;
      props.setProperty('zeruel_nonces', JSON.stringify(nonces));
      const key = 'probe_' + data.id;
      let record = JSON.parse(props.getProperty(key) || 'null');
      if (data.action === 'get') return reply({ok:true,record});
      const active = JSON.parse(props.getProperty('zeruel_active') || 'null');
      if (data.action === 'claim') {
        if (record && record.state !== 'active') return reply({ok:true,claimed:false,record});
        if (active && active.expires > now) return reply({ok:true,claimed:false,record:{id:active.id,state:'active'}});
        const latest = Number(props.getProperty('zeruel_last_run') || '0');
        if (now-latest < 30) return reply({ok:true,claimed:false,record:{state:'paused_cooldown'}});
        const keys = Object.keys(props.getProperties()).filter(k=>k.startsWith('probe_'));
        if (keys.length >= 50 && !record) return reply({ok:true,claimed:false,record:{state:'paused_storage_limit'}});
        record = {id:data.id,state:'active',started:now,cloud_gate_passed:false};
        props.setProperty('zeruel_active', JSON.stringify({id:data.id,expires:now+180}));
        props.setProperty('zeruel_last_run', String(now));
        props.setProperty(key, JSON.stringify(record));
        return reply({ok:true,claimed:true,record});
      }
      if (!record || record.state !== 'active' || !active || active.id !== data.id || active.expires < now)
        return reply({ok:false});
      const report = data.report;
      const states = ['synthetic_success','blocked_auth','blocked_paid_auth','blocked_cli_missing',
                      'paused_timeout','paused_quota','failed_cli','failed_response','failed_runtime'];
      if (!report || !states.includes(report.state)) return reply({ok:false});
      // Whitelist fields. Never persist arbitrary model text or credentials.
      record = {id:data.id,state:report.state,completed:now,cloud_gate_passed:false};
      for (const field of ['elapsed_seconds','children_peak_rss_kib','children_cpu_seconds'])
        if (typeof report[field] === 'number' && Number.isFinite(report[field]) && report[field]>=0)
          record[field] = report[field];
      if (report.state === 'synthetic_success') record.result = {marker:'ZERUEL_OK',sum:42};
      props.setProperty(key, JSON.stringify(record));
      props.deleteProperty('zeruel_active');
      return reply({ok:true,record});
    } finally {lock.releaseLock();}
  } catch (_) {return reply({ok:false});}
}
