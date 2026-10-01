// Measures the local detector on held-out synthetic documents. Prints only aggregate numbers.
// "Fuga" = a ground-truth personal span with characters neither detected nor sent to review.
import {generateCorpus} from './synth-generator.js';
import {detectPII} from '../pii-detector.js';

const NAME = t => (t.startsWith('NOMBRE_') ? 'NOMBRE' : t);
const count = Number(process.argv[2] || 300), seed = Number(process.argv[3] || 7919);
const stats = new Map();
const row = t => { if (!stats.has(t)) stats.set(t, {gold: 0, exact: 0, covered: 0, leak: 0}); return stats.get(t); };
let predicted = 0, falsePositive = 0, reviewTokens = 0;

for (const doc of generateCorpus(count, seed)) {
  const {spans, review} = detectPII(doc.text);
  predicted += spans.length; reviewTokens += review.length;
  for (const g of doc.spans) {
    const r = row(NAME(g.type)); r.gold++;
    const typed = spans.filter(s => s.start < g.end && s.end > g.start && NAME(s.type) === NAME(g.type));
    if (typed.some(s => s.start === g.start && s.end === g.end)) r.exact++;
    let leaked = false, covered = true;
    for (let i = g.start; i < g.end; i++) {
      if (/\s/.test(doc.text[i])) continue;
      const det = spans.some(s => i >= s.start && i < s.end);
      const rev = review.some(s => i >= s.start && i < s.end);
      if (!det) covered = false;
      if (!det && !rev) leaked = true;
    }
    if (covered) r.covered++;
    if (leaked) r.leak++;
  }
  for (const s of spans) if (!doc.spans.some(g => s.start < g.end && s.end > g.start)) falsePositive++;
}

console.log(`documentos=${count} semilla=${seed}`);
let gold = 0, leak = 0, covered = 0;
for (const [type, r] of [...stats].sort()) {
  gold += r.gold; leak += r.leak; covered += r.covered;
  console.log(`${type.padEnd(11)} total=${String(r.gold).padStart(5)} cubierto=${(100 * r.covered / r.gold).toFixed(1)}% exacto=${(100 * r.exact / r.gold).toFixed(1)}% fugas=${r.leak}`);
}
console.log(`TOTAL       total=${gold} cubierto=${(100 * covered / gold).toFixed(2)}% fugas=${leak} (${(100 * leak / gold).toFixed(3)}%)`);
console.log(`falsos_positivos=${falsePositive} de ${predicted} detecciones (${(100 * falsePositive / Math.max(1, predicted)).toFixed(1)}%), tokens_a_revisar=${reviewTokens} (${(reviewTokens / count).toFixed(1)}/doc)`);
