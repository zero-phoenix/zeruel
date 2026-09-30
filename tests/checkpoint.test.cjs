const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const source = fs.readFileSync('apps-script/SyntheticCheckpoint.gs','utf8');
const key = 'synthetic-fixture-key-not-a-real-secret-000';
function runtime(properties = new Map([['ZERUEL_CHECKPOINT_SECRET',key],['ZERUEL_OWNER_EMAIL','owner@example.test']])) {
  let locked = false;
  let identity = 'owner@example.test';
  const context = vm.createContext({Date,JSON,Number,Object,
    Session:{getEffectiveUser:()=>({getEmail:()=>identity})},
    ContentService:{MimeType:{JSON:'json'},createTextOutput:s=>({setMimeType:()=>JSON.parse(s)})},
    Utilities:{Charset:{UTF_8:'utf8'},computeHmacSha256Signature:(m,k)=>[...crypto.createHmac('sha256',k).update(m).digest()]},
    PropertiesService:{getScriptProperties:()=>({getProperty:k=>properties.get(k)||null,
      setProperty:(k,v)=>properties.set(k,v),deleteProperty:k=>properties.delete(k),
      getProperties:()=>Object.fromEntries(properties)})},
    LockService:{getScriptLock:()=>({tryLock:()=>{if(locked)return false;locked=true;return true},releaseLock:()=>{locked=false}})}
  });
  vm.runInContext(source,context);
  return {call:body=>context.runCheckpoint(body),publicCall:body=>context.doPost({postData:{contents:JSON.stringify(body)}}),setIdentity:v=>identity=v,properties};
}
function envelope(action,id,report=null) {
  const payload=JSON.stringify({action,id,report});
  const nonce=crypto.randomBytes(16).toString('hex'),timestamp=String(Math.floor(Date.now()/1000));
  const signature=crypto.createHmac('sha256',key).update(timestamp+'\n'+nonce+'\n'+payload).digest('hex');
  return {payload,nonce,timestamp,signature};
}
test('invalid signature cannot mutate storage',()=>{
  const r=runtime(),body=envelope('claim','a'.repeat(32));body.signature='0'.repeat(64);
  assert.equal(r.call(body).ok,false);assert.equal(r.properties.size,2);
});
test('replay is rejected',()=>{
  const r=runtime(),body=envelope('claim','a'.repeat(32));
  assert.equal(r.call(body).claimed,true);assert.equal(r.call(body).ok,false);
});
test('completed checkpoint survives fresh runtime and cannot execute twice',()=>{
  const r=runtime(),id='a'.repeat(32);
  assert.equal(r.call(envelope('claim',id)).claimed,true);
  const result=r.call(envelope('complete',id,{state:'synthetic_success',secret:'must not persist'}));
  assert.equal(result.ok,true);assert.equal(result.record.secret,undefined);
  const restarted=runtime(r.properties);
  assert.equal(restarted.call(envelope('get',id)).record.state,'synthetic_success');
  assert.equal(restarted.call(envelope('claim',id)).claimed,false);
});
test('global lease blocks simultaneous workers even with different IDs',()=>{
  const r=runtime();assert.equal(r.call(envelope('claim','a'.repeat(32))).claimed,true);
  assert.equal(r.call(envelope('claim','b'.repeat(32))).claimed,false);
});
test('expired authentication timestamp rejected',()=>{
  const r=runtime(),body=envelope('get','a'.repeat(32));body.timestamp='1000000000';
  assert.equal(r.call(body).ok,false);
});
test('unexpected result state cannot be persisted',()=>{
  const r=runtime(),id='a'.repeat(32);r.call(envelope('claim',id));
  assert.equal(r.call(envelope('complete',id,{state:'publish_secret'})).ok,false);
});

test('public web entry rejects even a valid signature',()=>{
  const r=runtime();assert.equal(r.publicCall(envelope('claim','a'.repeat(32))).ok,false);
  assert.equal(r.properties.size,2);
});
test('other Google identity and missing identity cannot write',()=>{
  const r=runtime();for(const email of ['other@example.test','']) {
    r.setIdentity(email);assert.equal(r.call(envelope('claim','a'.repeat(32))).ok,false);
  }
  assert.equal(r.properties.size,2);
});
test('missing owner configuration fails closed',()=>{
  const r=runtime();r.properties.delete('ZERUEL_OWNER_EMAIL');
  assert.equal(r.call(envelope('claim','a'.repeat(32))).ok,false);
});
