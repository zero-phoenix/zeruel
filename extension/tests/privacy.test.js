import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateEvent,validateExport,exportRecords,captureSVG,canRecord,today} from '../privacy.js';

const clean=()=>({seq:1,session:1,elapsed:350,site:1,tab:1,screen:1,action:'click',kind:'button',slot:1,decision:'none',point:{x:100,y:200},capture:{type:'structure',shapes:[{kind:'button',rect:{x:100,y:200,w:200,h:100}}],exclusions:[]}});
const envelope=event=>({schema:1,anonymization:'structural_only',events:[event]});
test('permite estructura y nunca datos de la página',()=>{
  const event=clean();assert.equal(validateEvent(event),event);
  const text=exportRecords([event]);assert.deepEqual(JSON.parse(text),envelope(event));
});
const personal=['María García','12345678','20123456789','Av. Ficticia 123','persona@example.test','987654321','EXP-2026-123456','POL-456789','ES9121000418450200051332','4111111111111111','S/ 1250.00','Contenido confidencial de un documento','Bearer fake-token-123'];
for(const secret of personal) {
  test(`rechaza dato ficticio libre: ${secret}`,()=>{
    for(const field of ['action','kind','decision']) {
      const event=clean();event[field]=secret;
      assert.throws(()=>exportRecords([event]));
    }
    const event=clean();event.text=secret;assert.throws(()=>validateExport(envelope(event)));
    const shape=clean();shape.capture.shapes[0].text=secret;assert.throws(()=>exportRecords([shape]));
  });
}
test('rechaza fuentes crudas, URLs, títulos, HTML, imágenes y campos adicionales recursivamente',()=>{
  for(const [key,value] of [['url','https://fake.test/persona/12345678'],['title','María García'],['value','12345678'],['html','<p>Datos</p>'],['screenshot','data:image/png;base64,FAKE'],['token','fake']]) {
    const event=clean();event[key]=value;assert.throws(()=>exportRecords([event]));
    const capture=clean();capture.capture[key]=value;assert.throws(()=>exportRecords([capture]));
  }
});
test('falla cerrada ante estructura corrupta, arrays extensos y prototipos',()=>{
  const event=clean();event.point.x=101;assert.throws(()=>validateEvent(event));
  const negative=clean();negative.slot=-1;assert.throws(()=>validateEvent(negative));
  const rectangle=clean();rectangle.capture.shapes[0].rect.w=1000;assert.throws(()=>validateEvent(rectangle));
  const nested=clean();nested.capture.exclusions=[{x:0,y:0,w:1000,h:1000,secret:'12345678'}];assert.throws(()=>validateEvent(nested));
  assert.throws(()=>validateExport(envelope(Object.create(clean()))));
  assert.throws(()=>exportRecords(Array(1001).fill(clean())));
  assert.throws(()=>exportRecords([clean(),clean()]));
});
test('remoto opaco no puede contener regiones visibles',()=>{
  const event=clean();event.capture.type='opaque';assert.throws(()=>validateEvent(event));
  event.capture.shapes=[];assert.doesNotThrow(()=>validateEvent(event));
  const image=captureSVG(event.capture);assert.equal(image.includes('text'),false);assert.equal(image.includes('image'),false);
});
test('SVG se reconstruye únicamente de números limitados y colores fijos',()=>{
  const text=captureSVG(clean().capture);
  assert.equal(text.includes('<text'),false);assert.equal(text.includes('<image'),false);assert.equal(text.includes('href'),false);
  const event=clean();event.capture.shapes[0].kind='<script>alert(1)</script>';assert.throws(()=>captureSVG(event.capture));
});
test('el día siguiente, pausa y generación vieja impiden guardar',()=>{
  const state={active:true,day:today(new Date(2026,8,30)),generation:3};
  assert.equal(canRecord(state,state.day,3),true);
  assert.equal(canRecord(state,today(new Date(2026,9,1)),3),false);
  assert.equal(canRecord(state,state.day,2),false);
  state.active=false;assert.equal(canRecord(state,state.day,3),false);
});
test('una decisión requiere acción específica y categoría fija',()=>{
  const event=clean();event.decision='admit';assert.throws(()=>validateEvent(event));
  event.action='decision';assert.doesNotThrow(()=>validateEvent(event));
});
test('manifiesto no concede permisos de sitios de forma global ni APIs de red/captura original',async()=>{
  const manifest=JSON.parse(await readFile(new URL('../manifest.json',import.meta.url),'utf8'));
  assert.equal(manifest.manifest_version,3);assert.equal(manifest.host_permissions,undefined);
  assert.equal(manifest.content_scripts,undefined);assert.equal(manifest.incognito,'not_allowed');
  assert.equal(manifest.permissions.includes('tabs'),false);assert.equal(manifest.permissions.includes('debugger'),false);
  assert.equal(manifest.permissions.includes('tabCapture'),false);
  assert.match(manifest.content_security_policy.extension_pages,/connect-src 'self';?$/);
  assert.equal(/https?:|\*/.test(manifest.content_security_policy.extension_pages),false);
});
test('código de observación no lee texto ni valores ni instala keylogger ni captura píxeles',async()=>{
  const source=await readFile(new URL('../content.js',import.meta.url),'utf8');
  assert.equal(/\.innerText\b|\.innerHTML\b|\.value\b|\.outerHTML\b|captureVisibleTab|captureStream|toDataURL|keydown|keyup|keypress|fetch\(/.test(source),false);
  const background=await readFile(new URL('../background.js',import.meta.url),'utf8');
  assert.equal(/captureVisibleTab|fetch\(|XMLHttpRequest|WebSocket/.test(background),false);
});
