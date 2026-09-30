// This boundary accepts structure only. No regex recognizer can safely anonymize arbitrary names.
export const ACTIONS = Object.freeze(['click', 'submit', 'navigation', 'tab_switch', 'decision']);
export const KINDS = Object.freeze(['button', 'link', 'field', 'select', 'form', 'table', 'surface', 'other']);
export const DECISIONS = Object.freeze(['none', 'continue', 'correct', 'request_information', 'admit', 'reject', 'review']);
const MODES = ['dom', 'remote'];
function fail() { throw new Error('Registro rechazado: contiene datos fuera del esquema anónimo.'); }
function object(value, keys) {
  if (!value || Object.getPrototypeOf(value) !== Object.prototype ||
      Object.keys(value).sort().join('|') !== [...keys].sort().join('|')) fail();
}
function integer(value, max = 1000, min = 0) {
  if (!Number.isSafeInteger(value) || value < min || value > max) fail();
}
function member(value, values) { if (!values.includes(value)) fail(); }
export function validateRect(rect) {
  object(rect, ['x', 'y', 'w', 'h']);
  for (const value of Object.values(rect)) { integer(value); if (value % 10 !== 0) fail(); }
  if (rect.x + rect.w > 1000 || rect.y + rect.h > 1000) fail();
  return rect;
}
export function validateCapture(capture) {
  object(capture, ['type', 'shapes', 'exclusions']);
  member(capture.type, ['structure', 'opaque']);
  if (!Array.isArray(capture.shapes) || capture.shapes.length > 100 ||
      !Array.isArray(capture.exclusions) || capture.exclusions.length > 10) fail();
  for (const shape of capture.shapes) {
    object(shape, ['kind', 'rect']); member(shape.kind, KINDS); validateRect(shape.rect);
  }
  for (const rect of capture.exclusions) validateRect(rect);
  if (capture.type === 'opaque' && capture.shapes.length !== 0) fail();
  return capture;
}
export function validateEvent(event) {
  object(event, ['seq', 'session', 'elapsed', 'site', 'tab', 'screen', 'action', 'kind', 'slot', 'decision', 'point', 'capture']);
  integer(event.seq, 1000, 1); integer(event.session, 1000000, 1);
  integer(event.elapsed, 86400000); integer(event.site, 1000, 1); integer(event.tab, 1000, 1);
  integer(event.screen, 10000, 1); integer(event.slot, 200);
  member(event.action, ACTIONS); member(event.kind, KINDS); member(event.decision, DECISIONS);
  object(event.point, ['x', 'y']);
  for (const value of Object.values(event.point)) { integer(value); if (value % 10 !== 0) fail(); }
  validateCapture(event.capture);
  if (event.action !== 'decision' && event.decision !== 'none') fail();
  return event;
}
export function validateExport(value) {
  object(value, ['schema', 'anonymization', 'events']);
  member(value.schema, [1]); member(value.anonymization, ['structural_only']);
  if (!Array.isArray(value.events) || value.events.length > 1000) fail();
  let previous = 0;
  for (const event of value.events) { validateEvent(event); if (event.seq <= previous) fail(); previous = event.seq; }
  return value;
}
export function exportRecords(events) {
  return JSON.stringify(validateExport({schema: 1, anonymization: 'structural_only', events}), null, 2);
}
export function captureSVG(capture) {
  validateCapture(capture);
  // Reconstructed rasterizable view. Never sourced from webpage pixels, text, href or labels.
  const colors = {button:'#445577',link:'#446677',field:'#556655',select:'#665566',form:'#777777',table:'#666666',surface:'#111111',other:'#555555'};
  const boxes = capture.shapes.map(s => `<rect x="${s.rect.x}" y="${s.rect.y}" width="${s.rect.w}" height="${s.rect.h}" fill="${colors[s.kind]}"/>`);
  const masked = capture.exclusions.map(r => `<rect x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" fill="#000000"/>`);
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><rect width="1000" height="1000" fill="${capture.type === 'opaque' ? '#111111' : '#eeeeee'}"/>${boxes.join('')}${masked.join('')}</svg>`;
}
export function today(now = new Date()) {
  return `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()}`;
}
export function canRecord(state, day, generation) {
  return state.active === true && state.day === day && state.generation === generation;
}
