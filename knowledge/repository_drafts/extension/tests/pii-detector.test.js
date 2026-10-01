import test from 'node:test';
import assert from 'node:assert/strict';
import {detectPII} from '../pii-detector.js';
import {generateCorpus} from '../training/synth-generator.js';

// Every non-space character of a personal value must be detected or sent to owner review.
function leaks(text, values) {
  const {spans, review} = detectPII(text);
  const hit = i => spans.some(s => i >= s.start && i < s.end) || review.some(s => i >= s.start && i < s.end);
  return values.filter(value => {
    const start = text.indexOf(value);
    assert.notEqual(start, -1, `fixture sin ${value}`);
    for (let i = start; i < start + value.length; i++) if (!/\s/.test(text[i]) && !hit(i)) return true;
    return false;
  });
}

test('corpus sintético conocido: sin fugas (SIMULADA, mismo diccionario que el generador)', () => {
  for (const doc of generateCorpus(40, 31)) {
    const values = doc.spans.map(s => doc.text.slice(s.start, s.end));
    assert.deepEqual(leaks(doc.text, values), []);
  }
});

// Out of distribution: names, surnames, companies and phrasing absent from every dictionary.
const OOD = [
  ['Mediante escrito, el ciudadano Wilfredo Ccoyllo Yupanqui solicitó la devolución.', ['Wilfredo', 'Ccoyllo', 'Yupanqui']],
  ['La consumidora Nélida Ttito Huillca, identificada con DNI N.° 40817265, presentó su reclamo.', ['Nélida', 'Ttito', 'Huillca', '40817265']],
  ['Se notificó a Grupo Textil Amancaes S.A.C. en su domicilio de Jr. Pumacahua 455, Breña, el lunes.', ['Grupo Textil Amancaes S.A.C.', 'Jr. Pumacahua 455, Breña']],
  ['Firma: Abg. Edelmira Chuquimango Lluén, apoderada de la denunciante.', ['Edelmira', 'Chuquimango', 'Lluén']],
  ['DENUNCIANTE: YESSENIA KARINA QUILLAHUAMÁN PFOCCORI', ['YESSENIA', 'KARINA', 'QUILLAHUAMÁN', 'PFOCCORI']],
  ['El monto reclamado asciende a S/ 12,480.50 según la boleta B001-00045821.', ['S/ 12,480.50', 'B001-00045821']],
  ['Ella Pumayalli Soncco declaró ante la Comisión.', ['Ella', 'Pumayalli', 'Soncco']],
  ['Se tiene a la vista el contrato suscrito con La Vista Inmobiliaria S.A.C.', ['La Vista Inmobiliaria S.A.C.']],
];
test('fuera de distribución: nombres y empresas desconocidos se detectan o van a revisión', () => {
  for (const [text, values] of OOD) assert.deepEqual(leaks(text, values), [], text);
});

test('texto operativo sin identidad no genera detecciones', () => {
  const {spans} = detectPII('La Comisión considera que corresponde declarar improcedente la denuncia, toda vez que no se acreditó la relación de consumo.');
  assert.deepEqual(spans, []);
});

test('el género solo sale del documento, nunca del nombre', () => {
  const plain = detectPII('presentada por Rosa Quispe Mamani contra la empresa').spans.find(s => s.type.startsWith('NOMBRE_'));
  assert.equal(plain.type, 'NOMBRE_DESCONOCIDO');
  const explicit = detectPII('la señora Rosa Quispe Mamani, identificada').spans.find(s => s.type.startsWith('NOMBRE_'));
  assert.equal(explicit.type, 'NOMBRE_MUJER');
});
