import {extractLocalImage} from '../ocr-local.js';
// Test application shim for a localhost smoke test. Does not exercise extension APIs.
if (!globalThis.chrome?.runtime) globalThis.chrome={runtime:{getURL:path=>new URL(`../${path}`,location.href).href}};
document.getElementById('start').onclick=async()=>{
  const result=document.getElementById('result');
  const button=document.getElementById('start');button.disabled=true;
  const canvas=document.createElement('canvas');canvas.width=900;canvas.height=180;
  const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,900,180);ctx.fillStyle='black';ctx.font='48px Arial';ctx.fillText('ZERUEL PRUEBA 42',40,100);
  try {
    const image=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));
    const started=performance.now();
    const recognized=await extractLocalImage(image,{onProgress:value=>{result.textContent=`OCR ${Math.round(value*100)}%`;}});
    const matches=recognized.text.trim()==='ZERUEL PRUEBA 42';
    result.textContent=JSON.stringify({synthetic:true,match:matches,confidence:recognized.confidence,elapsedMs:Math.round(performance.now()-started),text:recognized.text.trim()},null,2);
  } catch {result.textContent='FALLO: OCR local no pudo completar la prueba sintética.';}
  finally {canvas.width=0;canvas.height=0;button.disabled=false;}
};
