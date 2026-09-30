const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const crypto = require('node:crypto');
const source = fs.readFileSync('apps-script/SyntheticCheckpoint.gs','utf8');
const key = 'synthetic-fixture-key-not-a-real-secret-000';
function runtime(properties = new Map([['ZERUEL_CHECKPOINT_SECRET',key],['ZERUEL_OWNER_EMAIL','owner@example.test']])) {
  let locked = false;
  let now = Date.now();
  let failure = null;
  let failAt = null;
  const writes = {};
  let identity = 'owner@example.test';
  const context = vm.createContext({Date:{now:()=>now},JSON,Number,Object,
    Session:{getEffectiveUser:()=>({getEmail:()=>identity})},
    ContentService:{MimeType:{JSON:'json'},createTextOutput:s=>({setMimeType:()=>JSON.parse(s)})},
    Utilities:{getUuid:()=>crypto.randomUUID(),Charset:{UTF_8:'utf8'},computeHmacSha256Signature:(m,k)=>[...crypto.createHmac('sha256',k).update(m).digest()]},
    PropertiesService:{getScriptProperties:()=>({getProperty:k=>properties.get(k)||null,
      setProperty:(k,v)=>{writes[k]=(writes[k]||0)+1;if(failure===k||(failAt&&failAt[0]===k&&failAt[1]===writes[k]))throw Error('storage');properties.set(k,v)},deleteProperty:k=>{if(failure===k)throw Error('storage');properties.delete(k)},
      getProperties:()=>Object.fromEntries(properties)})},
    LockService:{getScriptLock:()=>({tryLock:()=>{if(locked)return false;locked=true;return true},releaseLock:()=>{locked=false}})}
  });
  vm.runInContext(source,context);
  return {call:body=>context.runCheckpoint(body),publicCall:body=>context.doPost({postData:{contents:JSON.stringify(body)}}),setIdentity:v=>identity=v,setTime:v=>now=v,now:()=>now,fail:v=>failure=v,failWrite:(k,n)=>{writes[k]=0;failAt=[k,n]},properties};
}
function envelope(action,id,report=null,generation=null,extra={},clock=Date.now()) {
  const payload=JSON.stringify({action,id,report,generation,...extra});
  const nonce=crypto.randomBytes(16).toString('hex'),timestamp=String(Math.floor(clock/1000));
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
  const claim=r.call(envelope('claim',id));assert.equal(claim.claimed,true);
  const result=r.call(envelope('complete',id,{state:'synthetic_success',secret:'must not persist'},claim.generation));
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

for (const field of ['zeruel_active','zeruel_last_run']) test('partial claim at '+field+' pauses all inference',()=>{
  const r=runtime(),id='c'.repeat(32);r.fail(field);
  assert.equal(r.call(envelope('claim',id)).ok,false);r.fail(null);
  assert.equal(r.call(envelope('claim',id)).record.state,'paused_uncertain');
  assert.equal(r.call(envelope('claim','d'.repeat(32))).claimed,false);
});
test('lease expires exactly at deadline and cannot be reacquired or completed',()=>{
  const r=runtime(),id='e'.repeat(32),claim=r.call(envelope('claim',id));
  const record=JSON.parse(r.properties.get('probe_'+id));r.setTime(record.expires*1000);
  // Auth timestamp must follow the controlled clock as well.
  const make=(action,report=null)=>{const b=envelope(action,id,report,claim.generation);b.timestamp=String(record.expires);b.signature=crypto.createHmac('sha256',key).update(b.timestamp+'\n'+b.nonce+'\n'+b.payload).digest('hex');return b};
  assert.equal(r.call(make('claim')).record.state,'paused_uncertain');
  assert.equal(r.call(make('complete',{state:'synthetic_success'})).ok,false);
});
test('completion retry is idempotent after partial deletion; conflicting or stale token rejected',()=>{
  const r=runtime(),id='f'.repeat(32),claim=r.call(envelope('claim',id)),report={state:'synthetic_success'};
  r.fail('zeruel_active');assert.equal(r.call(envelope('complete',id,report,claim.generation)).ok,false);
  r.fail(null);const retry=r.call(envelope('complete',id,report,claim.generation));assert.equal(retry.ok,true);
  assert.equal(retry.record.generation,undefined);assert.equal(retry.record.fingerprint,undefined);
  assert.equal(r.call(envelope('complete',id,report,claim.generation)).ok,true);
  assert.equal(r.call(envelope('complete',id,{state:'failed_runtime'},claim.generation)).ok,false);
  assert.equal(r.call(envelope('complete',id,report,'0'.repeat(32))).ok,false);
});
test('failed completion write keeps original active record for persistence retry',()=>{
  const r=runtime(),id='b'.repeat(32),claim=r.call(envelope('claim',id));r.fail('probe_'+id);
  assert.equal(r.call(envelope('complete',id,{state:'failed_runtime'},claim.generation)).ok,false);
  r.fail(null);assert.equal(r.call(envelope('complete',id,{state:'failed_runtime'},claim.generation)).ok,true);
});

// Manual owner recovery. Envelopes follow the controlled clock.
const at=(r,action,id,report=null,generation=null,extra={})=>envelope(action,id,report,generation,extra,r.now());
const OWNER={confirm:'owner_worker_finished'};
function expired(id) {
  const r=runtime(),claim=r.call(envelope('claim',id));
  r.setTime(JSON.parse(r.properties.get('probe_'+id)).expires*1000);
  return {r,generation:claim.generation};
}
test('recovery refused while the original lease can still act',()=>{
  const r=runtime(),id='1'.repeat(32),claim=r.call(envelope('claim',id));
  assert.equal(r.call(envelope('recover',id,{state:'synthetic_success'},claim.generation,OWNER)).ok,false);
  assert.equal(r.call(envelope('recover',id,null,claim.generation,OWNER)).ok,false);
});
test('recovery needs explicit owner confirmation and exact generation',()=>{
  const {r,generation}=expired('2'.repeat(32)),id='2'.repeat(32);
  assert.equal(r.call(at(r,'recover',id,null,generation)).ok,false);
  assert.equal(r.call(at(r,'recover',id,null,'0'.repeat(32),OWNER)).ok,false);
  assert.equal(r.call(at(r,'recover','9'.repeat(32),null,generation,OWNER)).ok,false);
});
test('expired lease recovered with durable report is canonical, idempotent and frees only its lock',()=>{
  const id='3'.repeat(32),{r,generation}=expired(id),report={state:'synthetic_success',elapsed_seconds:5};
  assert.equal(r.call(at(r,'complete',id,report,generation)).ok,false);
  const first=r.call(at(r,'recover',id,report,generation,OWNER));
  assert.equal(first.ok,true);assert.equal(first.record.recovered,true);
  assert.equal(JSON.stringify(first.record.result),'{"marker":"ZERUEL_OK","sum":42}');
  assert.equal(first.record.generation,undefined);assert.equal(first.record.fingerprint,undefined);
  assert.equal(r.properties.has('zeruel_active'),false);
  assert.equal(r.call(at(r,'recover',id,report,generation,OWNER)).ok,true);
  assert.equal(r.call(at(r,'complete',id,report,generation)).ok,true);
  assert.equal(r.call(at(r,'recover',id,{state:'failed_runtime'},generation,OWNER)).ok,false);
  assert.equal(r.call(at(r,'recover',id,null,generation,OWNER)).ok,false);
  assert.equal(r.call(at(r,'claim',id)).claimed,false);
});
test('recovery without report is a terminal unknown tombstone, never success',()=>{
  const id='4'.repeat(32),{r,generation}=expired(id);
  const closed=r.call(at(r,'recover',id,null,generation,OWNER));
  assert.equal(closed.record.state,'terminal_unknown');assert.equal(closed.record.result,undefined);
  assert.equal(r.call(at(r,'complete',id,{state:'synthetic_success'},generation)).ok,false);
  assert.equal(r.call(at(r,'claim',id)).record.state,'terminal_unknown');
  assert.equal(r.call(at(r,'get',id)).record.state,'terminal_unknown');
});
test('stale worker cannot complete its closed ID or a newer lease',()=>{
  const old='5'.repeat(32),next='6'.repeat(32),{r,generation}=expired(old);
  r.call(at(r,'recover',old,null,generation,OWNER));r.setTime(r.now()+31000);
  const claim=r.call(at(r,'claim',next));assert.equal(claim.claimed,true);
  assert.notEqual(claim.generation,generation);
  assert.equal(r.call(at(r,'complete',old,{state:'synthetic_success'},generation)).ok,false);
  assert.equal(r.call(at(r,'complete',next,{state:'synthetic_success'},generation)).ok,false);
  assert.equal(r.call(at(r,'recover',next,null,generation,OWNER)).ok,false);
  assert.equal(JSON.parse(r.properties.get('zeruel_active')).id,next);
});
test('second claim write failure never authorizes and owner recovery unblocks',()=>{
  const r=runtime(),id='7'.repeat(32);r.failWrite('probe_'+id,2);
  assert.equal(r.call(envelope('claim',id)).ok,false);r.fail(null);
  assert.equal(r.call(envelope('get',id)).record.state,'paused_uncertain');
  assert.equal(r.call(envelope('claim','8'.repeat(32))).claimed,false);
  const generation=JSON.parse(r.properties.get('probe_'+id)).generation;
  r.setTime(JSON.parse(r.properties.get('zeruel_active')).expires*1000);
  assert.equal(r.call(at(r,'recover',id,null,generation,OWNER)).record.state,'terminal_unknown');
  assert.equal(r.call(at(r,'claim','8'.repeat(32))).claimed,true);
});
test('lost HTTP response after a stored completion is recovered by identical retry',()=>{
  const r=runtime(),id='a'.repeat(32),claim=r.call(envelope('claim',id)),report={state:'paused_quota'};
  r.call(envelope('complete',id,report,claim.generation)); // response lost by caller
  const retry=r.call(envelope('complete',id,report,claim.generation));
  assert.equal(retry.ok,true);assert.equal(retry.record.state,'paused_quota');
});
test('partial recovery write is retried idempotently',()=>{
  const id='b'.repeat(32),{r,generation}=expired(id);r.fail('zeruel_active');
  assert.equal(r.call(at(r,'recover',id,null,generation,OWNER)).ok,false);r.fail(null);
  assert.equal(r.call(at(r,'recover',id,null,generation,OWNER)).record.state,'terminal_unknown');
  assert.equal(r.properties.has('zeruel_active'),false);
});
