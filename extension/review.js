import {ENTITY_TYPES,prepareText,textExport,suggestSpans} from './text-anonymizer.js';
import {extractLocalImage} from './ocr-local.js';
const $=id=>document.getElementById(id);let spans=[],revision=0,selection={start:0,end:0};
for(const type of ENTITY_TYPES){const option=document.createElement('option');option.value=type;option.textContent=type;$('type').append(option);}
$('type').value='NOMBRE_DESCONOCIDO';
function refresh(){
  try{const review=prepareText($('original').value,spans);$('preview').value=review.preview;$('export').disabled=!review.ready||!$('original').value;
    $('status').textContent=review.ready?'Vocabulario y marcadores válidos. Revisa el resultado antes de exportar.':`${review.unreviewed.length} fragmentos no clasificados: exportación bloqueada.`;
  }catch{$('export').disabled=true;$('status').textContent='Selecciones inválidas: quítalas y vuelve a clasificar.';}
}
for(const event of ['select','keyup','mouseup'])$('original').addEventListener(event,()=>{selection={start:$('original').selectionStart,end:$('original').selectionEnd};});
$('original').addEventListener('input',()=>{revision++;spans=[];selection={start:0,end:0};$('suggestions').replaceChildren();refresh();});
$('mark').onclick=()=>{
  const next=[...spans,{...selection,type:$('type').value}];
  try{prepareText($('original').value,next);spans=next;revision++;refresh();}
  catch{$('status').textContent='Selecciona un fragmento completo sin superponerlo con otras selecciones.';}
};
$('suggest').onclick=()=>{
  $('suggestions').replaceChildren();
  for(const proposed of suggestSpans($('original').value)){
    const button=document.createElement('button');button.textContent=`Revisar ${proposed.type}: posiciones ${proposed.start}–${proposed.end}`;
    button.onclick=()=>{$('original').focus();$('original').setSelectionRange(proposed.start,proposed.end);selection={start:proposed.start,end:proposed.end};$('type').value=proposed.type;};
    $('suggestions').append(button);
  }
};
$('reset').onclick=()=>{revision++;spans=[];refresh();};
function clear(){revision++;spans=[];$('original').value='';$('preview').value='';$('image').value='';$('suggestions').replaceChildren();selection={start:0,end:0};refresh();}
$('clear').onclick=clear;
$('export').onclick=()=>{
  try{const blob=new Blob([textExport($('original').value,spans)],{type:'application/json'}),url=URL.createObjectURL(blob),link=document.createElement('a');
    link.href=url;link.download='zeruel-texto-anonimizado.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }catch{$('export').disabled=true;$('status').textContent='Exportación bloqueada: falta clasificar información.';}
};
$('ocr').onclick=async()=>{
  const file=$('image').files[0];if(!file)return;
  const current=++revision;$('ocr').disabled=true;$('status').textContent='Procesando solo en esta PC…';
  try{const result=await extractLocalImage(file,{onProgress:()=>{if(revision===current)$('status').textContent='OCR local en curso; no hay envíos.';}});
    if(revision!==current)return;
    spans=[];$('original').value=result.text;$('image').value='';refresh();$('status').textContent+=' OCR pendiente de revisión completa; confianza no garantiza anonimización.';
  }catch{if(revision===current)$('status').textContent='OCR no disponible o falló. No se guardó ninguna imagen. Puedes pegar texto y clasificarlo localmente.';}
  finally{$('ocr').disabled=false;}
};
addEventListener('pagehide',clear);refresh();
