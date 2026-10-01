// Local, layered PII detector for Indecopi-style documents. Runs fully offline; never stores,
// logs or sends text. Layers: structured patterns with legal context, company suffixes and lists,
// Peruvian name/surname dictionaries with "names first, two surnames last" convention, address
// cues, and a fail-closed sweep that sends every remaining capitalized token or long number to
// owner review. Gender comes only from explicit words in the document (señor/señora,
// identificado/identificada), never from the name. Detection is a proposal: export still goes
// through text-anonymizer, which blocks anything unclassified.
import {FIRST_NAMES_M, FIRST_NAMES_F, SURNAMES, COMPANIES} from './training/synth-generator.js';

const norm = s => s.normalize('NFKC').toLocaleLowerCase('es');
const FIRST = new Set([...FIRST_NAMES_M, ...FIRST_NAMES_F].map(norm));
const LAST = new Set(SURNAMES.flatMap(s => s.split(' ')).map(norm).filter(w => !['de', 'del', 'la', 'los', 'las'].includes(w)));
const KNOWN_COMPANIES = COMPANIES.map(norm);
const CONNECTORS = new Set(['de', 'del', 'la', 'las', 'los']);
const INSTITUTIONAL = new Set(('lima resolución final expediente denunciante denunciada denunciado materia sumilla protección consumidor antecedentes análisis se resuelve primero segundo tercero declarar comisión comisionados secretaría técnica código defensa indecopi sala tribunal mediante asimismo para en con la el los las una un su sus del de por que y no es al lo como toda vez esta este conforme señor señora señores sr sra don doña ruc dni distrito av jr calle pasaje mz lt urb seguros reaseguros compañía banco financiera caja municipal ahorro clínica eps inversiones transportes aseguradora inmobiliaria perú').split(' '));
const WORD = /[\p{Lu}][\p{L}\p{M}'’-]*|(?<=\s)(?:de|del|la|las|los)(?=\s)/gu;

function add(found, start, end, type, confidence) {
  if (end <= start) return;
  for (const s of found) if (start < s.end && end > s.start) return; // earlier layer wins
  found.push({start, end, type, confidence});
}
function each(text, regex, fn) { for (const m of text.matchAll(regex)) fn(m); }

function structured(text, found) {
  each(text, /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, m => add(found, m.index, m.index + m[0].length, 'CORREO', 0.99));
  each(text, /(?:S\/\.?|US\$|\$|€)\s?\d[\d.,]*\d/g, m => add(found, m.index, m.index + m[0].length, 'MONTO', 0.97));
  each(text, /\b(?:\d{4}[ -]){3}\d{1,7}\b|\b\d{16}\b/g, m => add(found, m.index, m.index + m[0].length, 'TARJETA', 0.95));
  each(text, /(?<=\bcuenta(?:\s+(?:de\s+ahorros|corriente|bancaria))?\s+N\.?\s?[°º]?\s?)[\d-]{6,30}\d/gi, m => add(found, m.index, m.index + m[0].length, 'CUENTA', 0.95));
  each(text, /(?<=\bcr[ée]dito(?:\s+\p{L}+)?\s+N\.?\s?[°º]?\s?)[\dA-Z-]{5,30}/giu, m => add(found, m.index, m.index + m[0].length, 'CREDITO', 0.93));
  each(text, /(?<=\bp[óo]liza\s+N\.?\s?[°º]?\s?)[A-Z0-9-]{4,30}/gi, m => add(found, m.index, m.index + m[0].length, 'POLIZA', 0.95));
  each(text, /(?<=\bexpediente\s+N\.?\s?[°º]?\s?)\d{1,6}-\d{4}(?:\/[A-Z0-9-]+)?/gi, m => add(found, m.index, m.index + m[0].length, 'EXPEDIENTE', 0.98));
  each(text, /(?<=\bresoluci[óo]n(?:\s+final)?\s+N\.?\s?[°º]?\s?)\d{1,6}-\d{4}(?:\/[A-Z0-9-]+)?/gi, m => add(found, m.index, m.index + m[0].length, 'DOCUMENTO', 0.97));
  // Boletas/facturas/guías (B001-00045821, F002-123, E001-9) identify a transaction.
  each(text, /\b[BFEGT][A-Z0-9]{2,3}-\d{1,8}\b/g, m => add(found, m.index, m.index + m[0].length, 'DOCUMENTO', 0.92));
  each(text, /\b\d{1,6}-20\d{2}\/[A-Z][A-Z0-9-]*/g, m => add(found, m.index, m.index + m[0].length, 'EXPEDIENTE', 0.85));
  each(text, /\b(?:10|15|17|20)\d{9}\b/g, m => add(found, m.index, m.index + m[0].length, 'RUC', 0.96));
  each(text, /\b9\d{8}\b|\+51\s?\d{3}\s?\d{3}\s?\d{3}/g, m => add(found, m.index, m.index + m[0].length, 'TELEFONO', 0.94));
  each(text, /\b\d{8}\b/g, m => add(found, m.index, m.index + m[0].length, 'DNI', 0.93));
}

function companies(text, found) {
  const lower = norm(text);
  for (const company of KNOWN_COMPANIES) {
    let index = lower.indexOf(company);
    while (index !== -1) { add(found, index, index + company.length, 'EMPRESA', 0.97); index = lower.indexOf(company, index + 1); }
  }
  each(text, /(?<=\b(?:DENUNCIAD[OA]|PROVEEDORA?)\s*:\s*)[^\n]+/g, m => add(found, m.index, m.index + m[0].trimEnd().length, 'EMPRESA', 0.9));
  each(text, /(?:[\p{Lu}][\p{L}\p{M}.&'-]*\s+){1,7}?(?:S\.A\.A\.|S\.A\.C\.|S\.A\.|E\.I\.R\.L\.|S\.R\.L\.|S\.C\.R\.L\.)/gu,
    m => add(found, m.index, m.index + m[0].length, 'EMPRESA', 0.9));
}

function addresses(text, found) {
  const cue = /\b(?:con\s+domicilio\s+en|domiciliad[oa]\s+en|domicilio\s+(?:real\s+|procesal\s+|legal\s+)?en|direcci[óo]n\s*:)\s+/gi;
  each(text, cue, m => {
    const start = m.index + m[0].length, rest = text.slice(start);
    // Abbreviations (Av., Jr., N.°, Mz., Lt.) contain dots, so only a comma before a lowercase
    // non-address word, a line break, ";" or "(" ends the address.
    const stop = /,\s+(?!(?:mz|lt|urb|int|dpto|piso|distrito|provincia|departamento)\b)(?=\p{Ll})|\n|;|\(/gu.exec(rest);
    add(found, start, start + (stop ? stop.index : Math.min(rest.length, 160)), 'DIRECCION', 0.9);
  });
  each(text, /\b(?:Av\.|Avenida|Jr\.|Jir[óo]n|Calle|Pasaje|Psje\.)\s+[^\n;]{2,90}?(?=,\s+(?!(?:mz|lt|distrito)\b)\p{Ll}|;|\n|\.\s|$)/gu,
    m => add(found, m.index, m.index + m[0].length, 'DIRECCION', 0.8));
}

function genderAt(text, start) {
  const before = norm(text.slice(Math.max(0, start - 40), start));
  if (/(?:señora|sra\.|doña|identificada|la\s+denunciante)[\s,:]*$/.test(before)) return 'NOMBRE_MUJER';
  if (/(?:señor|sr\.|don|identificado|el\s+denunciante)[\s,:]*$/.test(before)) return 'NOMBRE_HOMBRE';
  return 'NOMBRE_DESCONOCIDO';
}
const PERSON_CUE = /(?:señor(?:a|es)?|sr\.|sra\.|srta\.|dr\.|dra\.|abg\.|abog\.|ing\.|lic\.|don|doña|ciudadan[oa]|consumidor[a]?|denunciante\s*:|presentada\s+por|interpuesta\s+por|comisionados\s*:|abogad[oa]|apoderad[oa]|a\s+favor\s+de)[\s,:]*$/;

function people(text, found) {
  const words = [...text.matchAll(WORD)].map(m => ({start: m.index, end: m.index + m[0].length, w: m[0], n: norm(m[0])}));
  let i = 0;
  while (i < words.length) {
    const run = [words[i]];
    let j = i + 1;
    while (j < words.length && /^ +$/.test(text.slice(run[run.length - 1].end, words[j].start))) { run.push(words[j]); j++; }
    while (run.length && CONNECTORS.has(run[run.length - 1].n)) run.pop();
    // Merge connector + following word ("De la Cruz", "Del Castillo") into one unit.
    const units = [];
    let pending = null;
    for (const w of run) {
      if (CONNECTORS.has(w.n)) { pending ||= {start: w.start, parts: []}; pending.parts.push(w.n); continue; }
      if (pending) { units.push({start: pending.start, end: w.end, n: w.n, parts: [...pending.parts, w.n]}); pending = null; }
      else units.push({start: w.start, end: w.end, n: w.n, parts: [w.n]});
    }
    const known = units.filter(u => FIRST.has(u.n) || LAST.has(u.n)).length;
    // "Segundo", "Paz" or "Cruz" are both ordinary words and Peruvian names: a dictionary name
    // never disqualifies a run, otherwise "SEGUNDO ROJAS..." would leak.
    const institutional = units.some(u => INSTITUTIONAL.has(u.n) && !FIRST.has(u.n) && !LAST.has(u.n));
    const cue = units.length && PERSON_CUE.test(norm(text.slice(Math.max(0, units[0].start - 60), units[0].start)));
    if (units.length >= 2 && !institutional && (known >= 1 || cue)) {
      const gender = genderAt(text, units[0].start);
      const surnames = units.length >= 3 ? 2 : 1;
      units.forEach((u, k) => {
        const surname = (k >= units.length - surnames && !FIRST.has(u.n)) || u.parts.length > 1;
        add(found, u.start, u.end, surname ? 'APELLIDO' : gender, known ? 0.9 : 0.75);
      });
    }
    i = j;
  }
}

function sweep(text, found) {
  const covered = i => found.some(s => i >= s.start && i < s.end);
  const review = [];
  each(text, /[\p{Lu}][\p{L}\p{M}'’-]+|\d{5,}/gu, m => {
    if (covered(m.index)) return;
    const n = norm(m[0]);
    if (INSTITUTIONAL.has(n)) return;
    if (/^\d/.test(m[0])) { review.push({start: m.index, end: m.index + m[0].length, reason: 'numero_largo'}); return; }
    const name = FIRST.has(n) || LAST.has(n);
    const before = text.slice(Math.max(0, m.index - 8), m.index);
    // A title abbreviation ("Abg.", "Sra.", "Dr.") precedes a person, not a new sentence.
    const title = /\b(?:abg|abog|sr|sra|srta|dr|dra|ing|lic|mg|econ|cpc)\.\s+$/i.test(before);
    const sentenceStart = !title && (m.index === 0 || /(?:[.:;!?]\s+|\n\s*|\d+\.\s+)$/.test(before));
    if (!name && sentenceStart) return;
    if (!name && m[0].length > 3 && m[0] === m[0].toLocaleUpperCase('es')) return;
    review.push({start: m.index, end: m.index + m[0].length, reason: name ? 'nombre_posible' : 'mayuscula_desconocida'});
  });
  return review;
}

export function detectPII(text) {
  if (typeof text !== 'string' || text.length > 200000) throw new Error('Texto inválido para el detector.');
  const found = [];
  structured(text, found);
  companies(text, found);
  addresses(text, found);
  people(text, found);
  const review = sweep(text, found);
  found.sort((a, b) => a.start - b.start);
  return {spans: found, review};
}
