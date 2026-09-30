// Formatting metadata only. No page text, CSS URLs, font-file paths or document identifiers.
export const FONT_FAMILIES = ['Arial', 'Calibri', 'Times New Roman', 'Cambria', 'Verdana', 'Tahoma', 'Georgia', 'Courier New', 'sans-serif', 'serif', 'monospace', 'unknown'];
const ROLES = ['body', 'heading', 'header', 'footer', 'table_cell'];
const KEYS = ['role', 'font', 'fontSizePx', 'weight', 'italic', 'underline', 'lineHeightPx', 'alignment', 'marginTopPx', 'marginBottomPx', 'indentPx', 'page', 'xPx', 'yPx', 'widthPx', 'heightPx'];
function reject() { throw new Error('Formato rechazado: solo se admite metadata sin contenido personal.'); }
export function validateLayout(value) {
  if (!value || Object.getPrototypeOf(value) !== Object.prototype || Object.keys(value).sort().join('|') !== [...KEYS].sort().join('|')) reject();
  if (!ROLES.includes(value.role) || !FONT_FAMILIES.includes(value.font) || !['left', 'right', 'center', 'justify'].includes(value.alignment)) reject();
  if (typeof value.italic !== 'boolean' || typeof value.underline !== 'boolean') reject();
  for (const key of ['fontSizePx', 'lineHeightPx', 'marginTopPx', 'marginBottomPx', 'indentPx', 'xPx', 'yPx', 'widthPx', 'heightPx']) {
    if (!Number.isFinite(value[key]) || Math.abs(value[key]) > 10000) reject();
  }
  if (value.fontSizePx <= 0 || value.lineHeightPx <= 0 || value.widthPx < 0 || value.heightPx < 0) reject();
  if (!Number.isInteger(value.page) || value.page < 1 || value.page > 10000) reject();
  if (!Number.isInteger(value.weight) || value.weight < 1 || value.weight > 1000) reject();
  return value;
}
export function formattingCSS(value) {
  validateLayout(value);
  return {
    fontFamily: value.font === 'unknown' ? 'sans-serif' : value.font,
    fontSize: `${value.fontSizePx}px`, fontWeight: String(value.weight),
    fontStyle: value.italic ? 'italic' : 'normal', textDecoration: value.underline ? 'underline' : 'none',
    lineHeight: `${value.lineHeightPx}px`, textAlign: value.alignment,
    marginTop: `${value.marginTopPx}px`, marginBottom: `${value.marginBottomPx}px`, textIndent: `${value.indentPx}px`,
  };
}
