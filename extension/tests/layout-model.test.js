import test from 'node:test';
import assert from 'node:assert/strict';
import {validateLayout, formattingCSS} from '../layout-model.js';
const footer = () => ({role:'footer',font:'Times New Roman',fontSizePx:12,weight:400,italic:false,underline:false,lineHeightPx:18,alignment:'center',marginTopPx:6,marginBottomPx:0,indentPx:0,page:1,xPx:50,yPx:1000,widthPx:600,heightPx:30});
test('modelo conserva metadata tipográfica y pie de página (fixture simulado)', () => {
  assert.equal(validateLayout(footer()).role,'footer');
  const css = formattingCSS(footer());
  assert.equal(css.fontFamily,'Times New Roman'); assert.equal(css.lineHeight,'18px');
  assert.equal(css.fontSize,'12px'); assert.equal(css.textAlign,'center');
});
test('rechaza texto personal, CSS arbitrario y archivos de fuente privados (fixture ficticio)', () => {
  for (const changed of [{name:'Persona Ficticia'}, {font:'Persona Ficticia'}, {font:'url(https://example.invalid/private)'}, {fontSizePx:'12345678'}, {page:Infinity}]) {
    assert.throws(()=>validateLayout({...footer(),...changed}));
  }
});
test('fuente desconocida queda explícita, no se declara copia exacta', () => {
  const value={...footer(),font:'unknown'};
  assert.equal(validateLayout(value).font,'unknown'); assert.equal(formattingCSS(value).fontFamily,'sans-serif');
});
