import {test} from 'node:test';import assert from 'node:assert/strict';import {readFile} from 'node:fs/promises';import vm from 'node:vm';
test('DOM simulado: exclusión elimina geometría JSON, login pausa y configuración tardía no reactiva',async()=>{
  const source=await readFile(new URL('../content.js',import.meta.url),'utf8');
  const messages=[],handlers={};let listener,password=false;
  function element(tag='DIV',box={left:0,top:0,width:1,height:1}){
    return {tagName:tag,style:{},isConnected:false,append(){},attachShadow(){return {append(){}};},addEventListener(){},getBoundingClientRect(){return box;},closest(){return this;}};
  }
  const hidden=element('INPUT',{left:200,top:200,width:200,height:100}),visible=element('BUTTON',{left:700,top:500,width:100,height:100});
  Object.defineProperty(hidden,'value',{get(){throw new Error('No leer valor privado');}});
  const context={document:{createElement:element,documentElement:{append(node){node.isConnected=true;}},querySelector(){return password?{}:null;},querySelectorAll(){return [hidden,visible];},addEventListener(type,fn){handlers[type]=fn;}},
    chrome:{runtime:{onMessage:{addListener(fn){listener=fn;}},sendMessage(message){messages.push(message);return Promise.resolve({});}}},
    location:{pathname:'/fixture',search:'',hash:''},innerWidth:1000,innerHeight:1000,addEventListener(){},setTimeout(){},setInterval(){return 1;},clearInterval(){}};
  vm.runInNewContext(source,context);
  const config={type:'configure',epoch:'fixture',active:true,generation:1,mode:'dom',exclusions:[{x:100,y:100,w:500,h:300}],remoteConfirmed:false};
  listener(config);
  handlers.click({clientX:750,clientY:550,target:visible});
  const event=messages.find(message=>message.type==='event');assert.ok(event);
  assert.equal(event.capture.shapes.length,1);assert.equal(event.capture.shapes[0].kind,'button');
  listener({...config,active:false,generation:2});listener(config);
  handlers.click({clientX:750,clientY:550,target:visible});assert.equal(messages.filter(message=>message.type==='event').length,1);
  password=true;listener({...config,generation:3});
  assert.ok(messages.some(message=>message.type==='pause'));
  handlers.click({clientX:750,clientY:550,target:visible});assert.equal(messages.filter(message=>message.type==='event').length,1);
});
