import {test} from 'node:test';import assert from 'node:assert/strict';
import {ENTITY_TYPES,prepareText,anonymizeReviewedText,validateAnonymousText,textExport,suggestSpans} from '../text-anonymizer.js';
const span=(text,value,type)=>({start:text.indexOf(value),end:text.indexOf(value)+value.length,type});
test('texto local con spans conserva vocabulario y reemplaza nombres/documentos',()=>{
  const text='Revisar expediente EXP-2026-42 de María Pérez.';
  const spans=[span(text,'Revisar expediente','TEXTO_OPERATIVO'),span(text,'EXP-2026-42','EXPEDIENTE'),span(text,'de','TEXTO_OPERATIVO'),span(text,'María','NOMBRE_MUJER'),span(text,'Pérez','APELLIDO')];
  const output=anonymizeReviewedText(text,spans);
  assert.equal(output,'Revisar expediente EXPEDIENTE_1 de NOMBRE_MUJER_1 APELLIDO_1.');
  const exported=textExport(text,spans);for(const secret of ['María','Pérez','2026-42'])assert.equal(exported.includes(secret),false);
});
test('todos los marcadores tipados son seleccionados explícitamente, género no se infiere',()=>{
  for(const type of ENTITY_TYPES.filter(type=>type!=='TEXTO_OPERATIVO')){assert.equal(anonymizeReviewedText('Privado',[{start:0,end:7,type}]),`${type}_1`);}
  assert.equal(anonymizeReviewedText('Alex',[{start:0,end:4,type:'NOMBRE_DESCONOCIDO'}]),'NOMBRE_DESCONOCIDO_1');
});
test('entidad repetida comparte alias dentro de llamada y no expone mapa reversible',()=>{
  const text='María y María';const out=prepareText(text,[{start:0,end:5,type:'NOMBRE_DESCONOCIDO'},{start:6,end:7,type:'TEXTO_OPERATIVO'},{start:8,end:13,type:'NOMBRE_DESCONOCIDO'}]);
  assert.equal(out.preview,'NOMBRE_DESCONOCIDO_1 y NOMBRE_DESCONOCIDO_1');assert.equal(out.mapping,undefined);
});
test('bloquea cualquier fragmento no revisado, identificadores y texto arbitrario',()=>{
  for(const text of ['Revisar María','DNI 12345678','persona@example.test','S/ 2500.00','Av. Ficticia 123','tokenabc123','كلمة سر','Bearer secret']){
    assert.equal(prepareText(text).ready,false);assert.throws(()=>anonymizeReviewedText(text));assert.throws(()=>textExport(text));
  }
});
test('rechaza spans vacíos, superpuestos, límites malos, tipos libres y campos extra',()=>{
  const bad=[{start:0,end:0,type:'DNI'},{start:-1,end:2,type:'DNI'},{start:0,end:100,type:'DNI'},{start:0,end:1,type:'PERSONA'},{start:0,end:1,type:'DNI',value:'12345678'}];
  for(const value of bad)assert.throws(()=>prepareText('texto',[value]));
  assert.throws(()=>prepareText('abcdef',[{start:0,end:4,type:'DNI'},{start:3,end:5,type:'RUC'}]));
  assert.throws(()=>prepareText('😀',[{start:0,end:1,type:'DOCUMENTO'}]));
});
test('sugerencias no son aprobación y no adivinan nombres/género',()=>{
  const text='DNI 12345678 y correo ficticio@example.test';const suggestions=suggestSpans(text);
  assert.deepEqual(suggestions.map(s=>s.type),['DNI','CORREO']);
  assert.equal(prepareText(text).ready,false);assert.equal(suggestSpans('María').length,0);
});
test('exportación rechaza marcadores inválidos y código/datos adicionales',()=>{
  for(const text of ['NOMBRE_MUJER_0','NOMBRE_MUJER_1@example.test','<script>Revisar</script>','TARJETA_1 4111111111111111'])assert.throws(()=>validateAnonymousText(text));
  assert.doesNotThrow(()=>validateAnonymousText('Revisar DOCUMENTO_1.'));
});
test('regresión: vocabulario corriente no aprueba Ella ni La Vista sin spans',()=>{
  for(const text of ['Ella','La Vista','Revisar expediente']){
    assert.equal(prepareText(text).ready,false);assert.throws(()=>textExport(text));
  }
  assert.equal(anonymizeReviewedText('Ella',[{start:0,end:4,type:'NOMBRE_DESCONOCIDO'}]),'NOMBRE_DESCONOCIDO_1');
  assert.equal(anonymizeReviewedText('La Vista',[{start:0,end:8,type:'EMPRESA'}]),'EMPRESA_1');
  assert.equal(anonymizeReviewedText('Revisar expediente',[{start:0,end:18,type:'TEXTO_OPERATIVO'}]),'Revisar expediente');
  assert.throws(()=>anonymizeReviewedText('María',[{start:0,end:5,type:'TEXTO_OPERATIVO'}]));
});
