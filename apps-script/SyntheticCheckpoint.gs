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
    if (!/^[a-f0-9]{32}$/.test(data.id) || !['get','claim','complete','recover'].includes(data.action))
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
      const publicRecord = value => {
        if (!value) return null;
        const result = {};
        for (const field of ['id','state','started','completed','elapsed_seconds',
                             'children_peak_rss_kib','children_cpu_seconds','result','recovered'])
          if (value[field] !== undefined) result[field] = value[field];
        result.cloud_gate_passed = false;
        return result;
      };
      const active = JSON.parse(props.getProperty('zeruel_active') || 'null');
      const validLease = record && record.state === 'active' && active &&
        active.id === data.id && active.generation === record.generation &&
        active.expires === record.expires && active.expires > now;
      if (record && (record.state === 'preparing' || (record.state === 'active' && !validLease)))
        record = {...record,state:'paused_uncertain'};
      if (data.action === 'get') return reply({ok:true,record:publicRecord(record)});
      if (data.action === 'claim') {
        if (record) return reply({ok:true,claimed:false,record:publicRecord(record)});
        // Any incomplete global lease is uncertain, even after its deadline.
        if (active) {
          const ownerRecord = JSON.parse(props.getProperty('probe_' + active.id) || 'null');
          const coherent = ownerRecord && ownerRecord.state === 'active' &&
            ownerRecord.generation === active.generation && ownerRecord.expires === active.expires;
          return reply({ok:true,claimed:false,record:{id:active.id,
            state:coherent && active.expires > now ? 'active' : 'paused_uncertain',cloud_gate_passed:false}});
        }
        const latest = Number(props.getProperty('zeruel_last_run') || '0');
        if (now-latest < 30) return reply({ok:true,claimed:false,record:{state:'paused_cooldown',cloud_gate_passed:false}});
        const keys = Object.keys(props.getProperties()).filter(k=>k.startsWith('probe_'));
        if (keys.some(k => { const value = JSON.parse(props.getProperty(k)); return value && ['active','preparing'].includes(value.state); }))
          return reply({ok:true,claimed:false,record:{state:'paused_uncertain',cloud_gate_passed:false}});
        if (keys.length >= 50) return reply({ok:true,claimed:false,record:{state:'paused_storage_limit',cloud_gate_passed:false}});
        const generation = Utilities.getUuid().replace(/-/g,'');
        record = {id:data.id,state:'preparing',started:now,expires:now+180,generation,cloud_gate_passed:false};
        // Persist the intent before granting a lease; partial writes never authorize inference.
        props.setProperty(key, JSON.stringify(record));
        props.setProperty('zeruel_active', JSON.stringify({id:data.id,expires:record.expires,generation}));
        props.setProperty('zeruel_last_run', String(now));
        record.state = 'active';
        props.setProperty(key, JSON.stringify(record));
        return reply({ok:true,claimed:true,generation,record:publicRecord(record)});
      }
      if (!record || typeof data.generation !== 'string' || data.generation !== record.generation)
        return reply({ok:false});
      const ownLease = active && active.id === data.id && active.generation === data.generation;
      const normalize = report => {
        const states = ['synthetic_success','blocked_auth','blocked_paid_auth','blocked_cli_missing',
                        'paused_timeout','paused_quota','failed_cli','failed_response','failed_runtime'];
        if (!report || !states.includes(report.state)) return null;
        // Whitelist fields. Never persist arbitrary model text or credentials.
        const normalized = {state:report.state,cloud_gate_passed:false};
        for (const field of ['elapsed_seconds','children_peak_rss_kib','children_cpu_seconds'])
          if (typeof report[field] === 'number' && Number.isFinite(report[field]) && report[field]>=0)
            normalized[field] = report[field];
        if (report.state === 'synthetic_success') normalized.result = {marker:'ZERUEL_OK',sum:42};
        return normalized;
      };
      if (data.action === 'recover') {
        // Manual owner recovery: never reached by the server, never grants a new inference.
        if (data.confirm !== 'owner_worker_finished') return reply({ok:false});
        if (ownLease && active.expires > now) return reply({ok:false});
        const normalized = data.report === null ? {state:'terminal_unknown',cloud_gate_passed:false}
                                                : normalize(data.report);
        if (!normalized) return reply({ok:false});
        const fingerprint = JSON.stringify(normalized);
        if (record.fingerprint !== undefined && record.fingerprint !== fingerprint) return reply({ok:false});
        if (record.fingerprint === undefined) {
          // Terminal record first: a failed lease deletion only leaves an idempotent retry.
          record = {id:data.id,...normalized,completed:now,generation:data.generation,fingerprint,recovered:true};
          props.setProperty(key, JSON.stringify(record));
        }
        if (ownLease) props.deleteProperty('zeruel_active');
        return reply({ok:true,record:publicRecord(record)});
      }
      const normalized = normalize(data.report);
      if (!normalized) return reply({ok:false});
      const fingerprint = JSON.stringify(normalized);
      if (record.fingerprint !== undefined) {
        if (record.fingerprint !== fingerprint) return reply({ok:false});
        if (ownLease) props.deleteProperty('zeruel_active');
        return reply({ok:true,record:publicRecord(record)});
      }
      if (!validLease) return reply({ok:false});
      record = {id:data.id,...normalized,completed:now,generation:data.generation,fingerprint};
      props.setProperty(key, JSON.stringify(record));
      props.deleteProperty('zeruel_active');
      return reply({ok:true,record:publicRecord(record)});
    } finally {lock.releaseLock();}
  } catch (_) {return reply({ok:false});}
}
