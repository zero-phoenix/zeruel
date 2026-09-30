import {validateExport,validateRect,captureSVG} from './privacy.js';
const $=id=>document.getElementById(id);let zones=[];
async function send(message) { const result=await chrome.runtime.sendMessage(message);if(result?.error)throw new Error(result.error);return result; }
async function refresh(){const info=await send({type:'status'});$('status').textContent=`${info.status} · ${info.count} registros locales`;$('mode').value=info.mode;}
function run(task){$('notice').textContent='';task().then(refresh).catch(()=>{$('notice').textContent='No se completó. Revisa el permiso del sitio y la configuración. La observación queda pausada.';void send({type:'pause'});});}
function zonesView(){$('zones').textContent=zones.length?`${zones.length} zonas configuradas para la próxima activación`:'Sin zonas';}
$('authorize').onclick=()=>run(async()=>{
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
  const url=new URL(tab.url);if(!['http:','https:'].includes(url.protocol)||url.username||url.password)throw new Error('Sitio no permitido');
  const accepted=await chrome.permissions.request({origins:[`${url.origin}/*`]});
  if(!accepted)throw new Error('Permiso no concedido');
});
$('activate').onclick=()=>run(()=>send({type:'activate',mode:$('mode').value,exclusions:zones,remoteConfirmed:$('remoteSafe').checked}));
$('pause').onclick=()=>run(()=>send({type:'pause'}));
$('addZone').onclick=()=>run(async()=>{
  if(zones.length>=10)throw new Error('Límite');
  const rect={x:Number($('x').value)*10,y:Number($('y').value)*10,w:Number($('w').value)*10,h:Number($('h').value)*10};
  validateRect(rect);zones.push(rect);zonesView();
});
$('clearZones').onclick=()=>{zones=[];zonesView();};
$('recordDecision').onclick=()=>run(()=>send({type:'decision',decision:$('decision').value}));
$('clear').onclick=()=>run(async()=>{if(confirm('¿Eliminar definitivamente los registros estructurales locales?'))await send({type:'clear'});});
async function exported(){const result=await send({type:'export'});return validateExport(JSON.parse(result.json));}
$('export').onclick=()=>run(async()=>{
  const data=await exported();const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download='zeruel-estructura-anonima.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
$('preview').onclick=()=>run(async()=>{
  const data=await exported();$('capture').replaceChildren();
  if(!data.events.length)return;
  const blob=new Blob([captureSVG(data.events.at(-1).capture)],{type:'image/svg+xml'}),url=URL.createObjectURL(blob);
  const image=document.createElement('img');image.alt='Captura estructural sin texto ni píxeles originales';image.src=url;image.onload=()=>URL.revokeObjectURL(url);$('capture').append(image);
});
void refresh();
