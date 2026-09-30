import {validateEvent, validateExport, validateCapture, validateRect, exportRecords, today, canRecord, DECISIONS} from './privacy.js';

// State deliberately starts paused whenever the MV3 worker restarts. Never persist consent to run.
const state = {active:false, day:'', generation:0, session:0, start:0, mode:'dom', exclusions:[], remoteConfirmed:false};
const epoch=crypto.randomUUID();
let queue = Promise.resolve();
let initialized = false;
let events = [];
const tabs = new Map();
const sites = new Map();
const throttles = new Map();
const init = (async () => {
  const stored = await chrome.storage.local.get(['records','sessionCounter']);
  try { events = validateExport(stored.records || {schema:1,anonymization:'structural_only',events:[]}).events; }
  catch { events=[]; await chrome.storage.local.remove('records'); }
  state.session = Number.isSafeInteger(stored.sessionCounter) && stored.sessionCounter < 1000000 ? stored.sessionCounter : 0;
  initialized=true;
  await badge('desconectado');
  await broadcast();
  await chrome.alarms.create('daily-stop', {periodInMinutes:1});
})();
function serial(job) { const result=queue.then(job); queue=result.catch(()=>{}); return result; }
async function badge(status) {
  const text={activo:'ACT',pausado:'PAU',desconectado:'OFF'}[status];
  await chrome.action.setBadgeText({text});
  await chrome.action.setBadgeBackgroundColor({color:status==='activo'?'#197343':'#666666'});
  await chrome.action.setTitle({title:`Zeruel: ${status}`});
}
function effective() { return state.active && state.day===today(); }
function stop() {
  state.active=false; state.generation++;
  void badge('pausado'); void broadcast();
}
async function authorized(tab) {
  if (!tab || !tab.url || !Number.isInteger(tab.id)) return false;
  try {
    const url=new URL(tab.url);
    if (!['https:','http:'].includes(url.protocol) || url.username || url.password) return false;
    return await chrome.permissions.contains({origins:[`${url.origin}/*`]});
  } catch { return false; }
}
async function tabStatus(tab) { return await authorized(tab) ? (effective()?'activo':'pausado') : 'desconectado'; }
async function configure(tab) {
  if (!await authorized(tab)) return;
  await chrome.tabs.sendMessage(tab.id,{type:'configure',epoch,active:effective(),generation:state.generation,mode:state.mode,exclusions:state.exclusions,remoteConfirmed:state.remoteConfirmed}).catch(()=>{});
}
async function broadcast() {
  const list=await chrome.tabs.query({});
  await Promise.allSettled(list.map(configure));
}
async function install(tab) {
  if (!await authorized(tab)) return;
  await chrome.scripting.executeScript({target:{tabId:tab.id},files:['content.js']}).catch(()=>{});
  await configure(tab);
}
function siteId(origin) { if(!sites.has(origin)) sites.set(origin,sites.size+1); return sites.get(origin); }
function tabId(id) { if(!tabs.has(id)) tabs.set(id,{id:tabs.size+1,screen:1}); return tabs.get(id); }
async function append(payload,sender,generation) {
  await init;
  if(!canRecord(state,today(),generation) || events.length>=1000) return;
  const tab=await chrome.tabs.get(sender.tab.id).catch(()=>null);
  if(!tab?.active || !await authorized(tab) || !canRecord(state,today(),generation)) return;
  if(payload.epoch!==epoch || payload.generation!==generation || !['click','submit','navigation','tab_switch','decision'].includes(payload.action)) return;
  // No fields of untrusted page message are spread or saved. Strict validation rejects extras in capture.
  validateCapture(payload.capture);
  const now=Date.now();
  if(['click','navigation','tab_switch'].includes(payload.action) && now-(throttles.get(tab.id)||0)<350) return;
  const alias=tabId(tab.id);
  if(payload.action==='navigation') alias.screen++;
  const event=validateEvent({seq:events.length+1,session:state.session,elapsed:Math.min(86400000,Math.max(0,now-state.start)),site:siteId(new URL(tab.url).origin),tab:alias.id,screen:alias.screen,action:payload.action,kind:payload.kind,slot:payload.slot,decision:payload.decision,point:payload.point,capture:payload.capture});
  if(state.mode==='remote' && (!state.remoteConfirmed || event.capture.type!=='opaque')) return;
  if(!canRecord(state,today(),generation)) return;
  throttles.set(tab.id,now);
  const next=[...events,event];
  // Only allowlisted structure crosses the persistence boundary.
  await chrome.storage.local.set({records:validateExport({schema:1,anonymization:'structural_only',events:next})});
  events=next;
  if(events.length>=1000) stop();
}
async function ui(message) {
  await init;
  if(message.type==='status') {
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    const status=await tabStatus(tab);
    await badge(status);
    return {status,count:events.length,mode:state.mode,day:state.day,authorized:await authorized(tab)};
  }
  if(message.type==='activate') {
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!await authorized(tab)) throw new Error('Autoriza primero este sitio.');
    if(events.length>=1000) throw new Error('Exporta y elimina los registros antes de seguir.');
    if(!['dom','remote'].includes(message.mode) || !Array.isArray(message.exclusions) || message.exclusions.length>10) throw new Error('Configuración inválida.');
    message.exclusions.forEach(validateRect);
    if(message.mode==='remote' && message.remoteConfirmed!==true) throw new Error('Confirma que el remoto ya salió del inicio de sesión.');
    stop();
    const activationGeneration=state.generation;
    await queue;
    if(state.generation!==activationGeneration) return {ok:false};
    state.session++; state.day=today(); state.start=Date.now(); state.mode=message.mode;
    state.exclusions=message.exclusions; state.remoteConfirmed=message.remoteConfirmed===true;
    sites.clear();tabs.clear();throttles.clear();
    await chrome.storage.local.set({sessionCounter:state.session});
    if(state.generation!==activationGeneration) return {ok:false};
    state.active=true;
    await install(tab); await broadcast(); await badge(await tabStatus(tab));
    return {ok:true};
  }
  if(message.type==='export') { await queue; return {json:exportRecords(events)}; }
  if(message.type==='clear') {
    stop(); await queue; events=[]; await chrome.storage.local.remove('records'); return {ok:true};
  }
  if(message.type==='decision') {
    if(!DECISIONS.includes(message.decision)||message.decision==='none') return;
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(await authorized(tab)) await chrome.tabs.sendMessage(tab.id,{type:'decision',decision:message.decision}).catch(()=>{});
    return {ok:true};
  }
}
chrome.runtime.onMessage.addListener((message,sender,respond)=>{
  // Reject website messages; only isolated extension scripts and own popup may call this API.
  if(sender.id!==chrome.runtime.id || !message || typeof message.type!=='string') return false;
  if(message.type==='pause') {
    stop(); Promise.all([init,queue]).then(()=>respond({ok:true})); return true;
  }
  let task;
  if(sender.tab) {
    if(message.type==='hello') task=init.then(()=>configure(sender.tab)).then(()=>({ok:true}));
    else if(message.type==='event' && sender.frameId===0) {
      const generation=state.generation;
      task=serial(()=>append(message,sender,generation)).then(()=>({ok:true}));
    } else return false;
  } else {
    if(sender.url!==chrome.runtime.getURL('popup.html')) return false;
    task=ui(message);
  }
  task.then(value=>respond(value || {ok:false})).catch(()=>{stop();respond({ok:false,error:'Operación detenida; revisa los permisos y el esquema privado.'});});
  return true;
});
chrome.tabs.onActivated.addListener(async info=>{
  await init;
  const tab=await chrome.tabs.get(info.tabId).catch(()=>null);
  await badge(await tabStatus(tab));
  if(await authorized(tab)) {
    await install(tab);
    await chrome.tabs.sendMessage(tab.id,{type:'record_switch'}).catch(()=>{});
  }
});
chrome.tabs.onUpdated.addListener(async (id,change,tab)=>{
  if(change.status==='complete') { await init; await install(tab); if(tab.active) await badge(await tabStatus(tab)); }
  else if(change.url) {
    await init;
    if(await authorized(tab)) await chrome.tabs.sendMessage(id,{type:'record_navigation'}).catch(()=>{});
    else if(tab.active) await badge('desconectado');
  }
});
chrome.permissions.onRemoved.addListener(()=>stop());
chrome.alarms.onAlarm.addListener(alarm=>{if(alarm.name==='daily-stop' && state.active && state.day!==today()) stop();});
chrome.runtime.onStartup.addListener(()=>{stop();});
