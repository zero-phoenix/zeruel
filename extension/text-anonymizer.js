// Offline, manual span review. No storage, telemetry, network, gender inference, or raw export.
export const ENTITY_TYPES=Object.freeze(['NOMBRE_HOMBRE','NOMBRE_MUJER','NOMBRE_DESCONOCIDO','APELLIDO','DNI','RUC','DIRECCION','CORREO','TELEFONO','EXPEDIENTE','POLIZA','CUENTA','TARJETA','CREDITO','EMPRESA','MONTO','DOCUMENTO','TEXTO_OPERATIVO']);
// This deliberately small operational vocabulary preserves only known words. Everything else is blocked.
const VOCABULARY=new Set(('a al ante con contra de del desde durante e el ella ellos en entre es esta este estos fue ha hasta la las lo los o para por que se sin sobre su sus un una y admisión admitir apelación archivo asunto atención continuar corregir corrección decisión declarar documento expediente fecha formulario improcedencia improcedente información ingresar notificación número parte petición procedimiento recepción rechazar recurso requerimiento resolución respuesta revisión revisar solicitar trámite verificar vista').split(' '));
for(const word of 'dni ruc cuenta tarjeta crédito póliza correo teléfono dirección apellido nombre empresa monto hombre mujer desconocido'.split(' '))VOCABULARY.add(word);
const SAFE_PUNCTUATION=/^[\s.,:;!?()[\]{}"'«»\-/]*$/u;
function reject(){throw new Error('Texto bloqueado: hay fragmentos no clasificados o una selección inválida.');}
function validBoundary(text,index){return !(index>0&&index<text.length&&/[\uD800-\uDBFF]/.test(text[index-1])&&/[\uDC00-\uDFFF]/.test(text[index]));}
function spansFor(text,spans){
  if(typeof text!=='string'||text.length>100000||!Array.isArray(spans)||spans.length>1000)reject();
  const sorted=spans.map(span=>{
    if(!span||Object.getPrototypeOf(span)!==Object.prototype||Object.keys(span).sort().join('|')!=='end|start|type'||!ENTITY_TYPES.includes(span.type)||!Number.isInteger(span.start)||!Number.isInteger(span.end)||span.start<0||span.end<=span.start||span.end>text.length||!validBoundary(text,span.start)||!validBoundary(text,span.end))reject();
    return {...span};
  }).sort((a,b)=>a.start-b.start);
  for(let i=1;i<sorted.length;i++)if(sorted[i].start<sorted[i-1].end)reject();
  return sorted;
}
function unknownFragments(text,offset=0,allowVocabulary=false){
  const unknown=[];
  const tokens=text.matchAll(/[\p{L}\p{M}]+|\d+|[^\p{L}\p{M}\d\s.,:;!?()[\]{}"'«»\-/]+/gu);
  for(const token of tokens){if(!allowVocabulary||!VOCABULARY.has(token[0].normalize('NFKC').toLocaleLowerCase('es')))unknown.push({start:offset+token.index,end:offset+token.index+token[0].length});}
  return unknown;
}
export function prepareText(text,spans=[]){
  const sorted=spansFor(text,spans), counters=new Map(),aliases=new Map(),unknown=[];
  let preview='',cursor=0;
  for(const span of sorted){
    const gap=text.slice(cursor,span.start);unknown.push(...unknownFragments(gap,cursor));preview+=gap;
    if(span.type==='TEXTO_OPERATIVO'){
      const approved=text.slice(span.start,span.end);
      if(unknownFragments(approved,0,true).length||!SAFE_PUNCTUATION.test(approved.replace(/[\p{L}\p{M}]+/gu,'')))reject();
      preview+=approved;cursor=span.end;continue;
    }
    // Mapping exists only inside this call, never returned or stored.
    const key=span.type+'\0'+text.slice(span.start,span.end).normalize('NFKC').trim().toLocaleLowerCase('es');
    if(!aliases.has(key)){const n=(counters.get(span.type)||0)+1;counters.set(span.type,n);aliases.set(key,`${span.type}_${n}`);}
    preview+=aliases.get(key);cursor=span.end;
  }
  preview+=text.slice(cursor);unknown.push(...unknownFragments(text.slice(cursor),cursor));
  return {preview,unreviewed:unknown,ready:unknown.length===0};
}
export function anonymizeReviewedText(text,spans=[]){
  const review=prepareText(text,spans);if(!review.ready)reject();validateAnonymousText(review.preview);return review.preview;
}
export function validateAnonymousText(text){
  if(typeof text!=='string'||text.length>100000)reject();
  const marker=new RegExp(`\\b(?:${ENTITY_TYPES.join('|')})_[1-9][0-9]{0,3}\\b`,'g');
  const withoutMarkers=text.replace(marker,'');
  if(unknownFragments(withoutMarkers,0,true).length)reject();
  const punctuation=withoutMarkers.replace(/[\p{L}\p{M}]+/gu,'');if(!SAFE_PUNCTUATION.test(punctuation))reject();
  return text;
}
export function textExport(original,spans=[]){return JSON.stringify({schema:2,anonymization:'manual_spans_closed_vocabulary',text:anonymizeReviewedText(original,spans)},null,2);}
export function suggestSpans(text){
  if(typeof text!=='string'||text.length>100000)reject();
  // Suggestions never approve/classify automatically. All entities, including names, require owner review.
  const found=[];
  const patterns=[['CORREO',/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi],['DNI',/(?<=\bDNI\s*[:#]?\s*)\d{8}\b/gi],['RUC',/(?<=\bRUC\s*[:#]?\s*)\d{11}\b/gi],['TARJETA',/(?<=\btarjeta\s*[:#]?\s*)[\d -]{13,23}/gi],['POLIZA',/(?<=\bp[oó]liza\s*[:#]?\s*)[A-Z0-9-]{4,30}/gi],['MONTO',/(?:S\/\s*|US\$\s*|\$\s*|€\s*)\d[\d.,]*/g]];
  for(const [type,pattern] of patterns)for(const match of text.matchAll(pattern))found.push({start:match.index,end:match.index+match[0].length,type});
  return found.sort((a,b)=>a.start-b.start).filter((span,index,array)=>index===0||span.start>=array[index-1].end);
}
