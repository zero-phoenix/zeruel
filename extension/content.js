(() => {
  if(globalThis.__zeruelStructureObserver) return;
  globalThis.__zeruelStructureObserver=true;
  let active=false, generation=0, epoch='', mode='dom', exclusions=[], remoteConfirmed=false;
  let heartbeat;
  const quantize=value=>Math.max(0,Math.min(1000,Math.round(value/10)*10));
  function rect(element) {
    const r=element.getBoundingClientRect(), width=Math.max(1,innerWidth),height=Math.max(1,innerHeight);
    const x=quantize(r.left/width*1000),y=quantize(r.top/height*1000);
    return {x,y,w:Math.min(1000-x,quantize(r.width/width*1000)),h:Math.min(1000-y,quantize(r.height/height*1000))};
  }
  function blocked() {
    if(document.querySelector('input[type="password"],input[autocomplete="current-password"],input[autocomplete="new-password"],input[autocomplete="one-time-code"]')) return true;
    // Only used transiently to suppress login pages. URL is never saved or sent.
    if(/(?:login|signin|sign-in|oauth|sso|auth|access_token|reset-password)/i.test(location.pathname+location.search+location.hash)) return true;
    return mode==='remote'&&!remoteConfirmed;
  }
  const host=document.createElement('div');
  host.id='zeruel-private-indicator'; host.style.cssText='position:fixed;right:8px;top:8px;z-index:2147483647;';
  const shadow=host.attachShadow({mode:'closed'});
  const box=document.createElement('div');box.style.cssText='background:#18232d;color:white;border:2px solid #fff;padding:8px;font:13px system-ui;box-shadow:0 2px 6px #333;';
  const label=document.createElement('span');
  const pause=document.createElement('button');pause.textContent='Pausar';pause.style.cssText='margin-left:8px;cursor:pointer;';
  box.append(label,pause);shadow.append(box);
  function show(status) { label.textContent=`Zeruel: ${status}`; if(!host.isConnected) document.documentElement.append(host); }
  function disconnected() { active=false;clearInterval(heartbeat);show('desconectado'); }
  pause.addEventListener('click',()=>{active=false;show('pausado');chrome.runtime.sendMessage({type:'pause'}).catch(disconnected);});
  function kind(element) {
    if(!element || element===host) return 'other';
    const tag=element.tagName;
    if(tag==='BUTTON') return 'button';if(tag==='A') return 'link';
    if(tag==='INPUT'||tag==='TEXTAREA') return 'field';if(tag==='SELECT') return 'select';
    if(tag==='FORM') return 'form';if(tag==='TABLE') return 'table';
    if(['CANVAS','IFRAME','VIDEO','IMG','SVG'].includes(tag)) return 'surface';return 'other';
  }
  function elements() { return [...document.querySelectorAll('button,a,input,textarea,select,form,table,canvas,iframe,video,img,svg')].slice(0,200); }
  function snapshot() {
    if(mode==='remote') return {type:'opaque',shapes:[],exclusions};
    const shapes=[];
    for(const element of elements()) {
      const r=rect(element);if(!r.w||!r.h) continue;
      // An exclusion removes geometry from the JSON too, not only pixels in a preview.
      if(exclusions.some(z=>r.x<z.x+z.w&&r.x+r.w>z.x&&r.y<z.y+z.h&&r.y+r.h>z.y)) continue;
      shapes.push({kind:kind(element),rect:r});if(shapes.length>=100) break;
    }
    return {type:'structure',shapes,exclusions};
  }
  function excluded(point) { return exclusions.some(r=>point.x>=r.x&&point.x<=r.x+r.w&&point.y>=r.y&&point.y<=r.y+r.h); }
  function record(action,event,decision='none') {
    if(!active || blocked()) {if(active&&blocked()){active=false;show('pausado');chrome.runtime.sendMessage({type:'pause'}).catch(disconnected);}return;}
    const point={x:quantize((event?.clientX||0)/Math.max(1,innerWidth)*1000),y:quantize((event?.clientY||0)/Math.max(1,innerHeight)*1000)};
    if(event?.target===host||excluded(point)) return;
    const target=event?.target?.closest?.('button,a,input,textarea,select,form,table,canvas,iframe,video,img,svg') || event?.target;
    const slot=Math.max(0,elements().indexOf(target)+1);
    const message={type:'event',epoch,generation,action,kind:mode==='remote'?'surface':kind(target),slot:mode==='remote'?0:slot,decision,point,capture:snapshot()};
    chrome.runtime.sendMessage(message).catch(disconnected);
  }
  document.addEventListener('click',event=>record('click',event),true);
  document.addEventListener('submit',event=>record('submit',event),true);
  addEventListener('popstate',()=>record('navigation'));
  addEventListener('hashchange',()=>record('navigation'));
  chrome.runtime.onMessage.addListener(message=>{
    if(message.type==='configure') {
      if(message.epoch===epoch && message.generation<generation) return;
      const wasActive=active, previousGeneration=generation;
      active=message.active===true;epoch=message.epoch;generation=message.generation;mode=message.mode;exclusions=message.exclusions;remoteConfirmed=message.remoteConfirmed;
      clearInterval(heartbeat);
      if(active&&blocked()) {active=false;chrome.runtime.sendMessage({type:'pause'}).catch(disconnected);}
      show(active?'activo':'pausado');
      // Clock/worker failure must become visible, even when no action occurs. No screenshots or polling network.
      heartbeat=setInterval(()=>chrome.runtime.sendMessage({type:'hello'}).catch(disconnected),5000);
      if(active&&(!wasActive||previousGeneration!==generation)) setTimeout(()=>record('navigation'),0);
    }
    if(message.type==='record_switch') record('tab_switch');
    if(message.type==='record_navigation') record('navigation');
    if(message.type==='decision') record('decision',null,message.decision);
  });
  show('desconectado');
  chrome.runtime.sendMessage({type:'hello'}).catch(disconnected);
  // Capture only structure on actual document creation; contains no text or source pixels.
  setTimeout(()=>record('navigation'),200);
})();
