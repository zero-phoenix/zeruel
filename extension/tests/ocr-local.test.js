import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {extractLocalImage} from '../ocr-local.js';

test('OCR local restringe rutas, desactiva caché y destruye worker (motor simulado)', async () => {
  let options, terminated = 0, closed = 0;
  globalThis.chrome = {runtime:{getURL:path=>`chrome-extension://synthetic/${path}`}};
  globalThis.createImageBitmap = async () => ({width:640,height:480,close(){closed++;}});
  globalThis.Tesseract = {async createWorker(language, engine, value){
    assert.equal(language,'spa'); assert.equal(engine,1); options=value;
    return {async recognize(){return {data:{text:'Texto ficticio que debe revisar el propietario',confidence:70}};},async terminate(){terminated++;}};
  }};
  const result = await extractLocalImage(new Blob(['synthetic'],{type:'image/png'}));
  assert.equal(result.confidence,70);
  assert.equal(options.cacheMethod,'none'); assert.equal(options.workerBlobURL,false);
  for (const name of ['workerPath','corePath','langPath']) assert.ok(options[name].startsWith('chrome-extension://synthetic/vendor/'));
  assert.equal(terminated,1); assert.equal(closed,1);
});

test('OCR libera worker tras error y permite otra tarea (motor simulado)', async () => {
  let terminated=0;
  globalThis.Tesseract={async createWorker(){return {async recognize(){throw new Error('synthetic');},async terminate(){terminated++;}};}};
  await assert.rejects(extractLocalImage(new Blob(['test'],{type:'image/png'})));
  await assert.rejects(extractLocalImage(new Blob(['test'],{type:'image/png'})));
  assert.equal(terminated,2);
});

test('OCR rechaza archivo y dimensiones antes de iniciar motor (simulado)', async () => {
  globalThis.Tesseract={createWorker(){assert.fail('No debe iniciar');}};
  await assert.rejects(extractLocalImage(new Blob(['test'],{type:'text/plain'})));
  globalThis.createImageBitmap=async()=>({width:3000,height:3000,close(){}});
  await assert.rejects(extractLocalImage(new Blob(['test'],{type:'image/png'})),/megapíxeles/);
});

test('adapter no persiste ni transmite imágenes/texto', async () => {
  const source=(await readFile(new URL('../ocr-local.js',import.meta.url),'utf8')).replace(/^\s*\/\/.*$/gm,'');
  assert.equal(/storage\.|localStorage|indexedDB|sendMessage|fetch\(|XMLHttpRequest|WebSocket/.test(source),false);
});
