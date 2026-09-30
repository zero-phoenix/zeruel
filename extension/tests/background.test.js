import {test} from 'node:test';
import assert from 'node:assert/strict';

test('worker simulado: permisos, guardado estructural, pausa, carreras, exportación y reinicio',async()=>{
  const tab={id:2,url:'https://fixture.test/trabajo',active:true};
  const store={};let listener;let allowed=false;let config;let waitCounter=null;
  const noopEvent={addListener(){}};
  const chrome={runtime:{id:'fixture-extension',getURL:p=>`chrome-extension://fixture-extension/${p}`,onMessage:{addListener(fn){listener=fn;}},onStartup:noopEvent},
    storage:{local:{async get(){return structuredClone(store);},async set(value){if(value.sessionCounter&&waitCounter)await waitCounter;Object.assign(store,structuredClone(value));},async remove(key){delete store[key];}}},
    action:{async setBadgeText(){},async setBadgeBackgroundColor(){},async setTitle(){}},
    tabs:{async query(){return [tab];},async get(){return tab;},async sendMessage(id,message){if(message.type==='configure')config=message;},onActivated:noopEvent,onUpdated:noopEvent},
    permissions:{async contains(){return allowed;},onRemoved:noopEvent},
    scripting:{async executeScript(){}},alarms:{async create(){},onAlarm:noopEvent}};
  globalThis.chrome=chrome;
  await import(`../background.js?fixture=${Date.now()}`);
  const popup={id:chrome.runtime.id,url:chrome.runtime.getURL('popup.html')};
  const content={id:chrome.runtime.id,tab,frameId:0};
  const send=(message,sender=popup)=>new Promise(resolve=>listener(message,sender,resolve));
  assert.equal((await send({type:'status'})).status,'desconectado');
  assert.equal((await send({type:'activate',mode:'dom',exclusions:[]})).ok,false);
  allowed=true;
  await send({type:'activate',mode:'dom',exclusions:[]});
  assert.equal((await send({type:'status'})).status,'activo');
  const event=()=>({type:'event',epoch:config.epoch,generation:config.generation,action:'click',kind:'button',slot:1,decision:'none',point:{x:100,y:100},capture:{type:'structure',shapes:[],exclusions:[]}});
  await send(event(),content);
  assert.equal(store.records.events.length,1);
  const stale=event();
  await send({type:'pause'});await send(stale,content);
  assert.equal(store.records.events.length,1);
  assert.equal((await send({type:'status'})).status,'pausado');
  // Falsifier: pause while activate is awaiting its durable counter must not reactivate.
  let release;
  waitCounter=new Promise(resolve=>release=resolve);
  const activating=send({type:'activate',mode:'dom',exclusions:[]});
  await new Promise(resolve=>setTimeout(resolve,10));
  await send({type:'pause'});release();await activating;waitCounter=null;
  assert.equal((await send({type:'status'})).status,'pausado');
  const exported=await send({type:'export'});
  assert.equal(exported.json.includes('fixture.test'),false);
  assert.equal(exported.json.includes('/trabajo'),false);
  // Worker reloaded with records retained must remain paused, not continue daily consent.
  await send({type:'activate',mode:'dom',exclusions:[]});
  await import(`../background.js?restart=${Date.now()}`);
  assert.equal((await send({type:'status'})).status,'pausado');
  assert.equal((await send({type:'status'})).count,1);
  await send({type:'clear'});
  assert.equal((await send({type:'status'})).count,0);
  delete globalThis.chrome;
});
