// Fictitious Indecopi-CC1-style documents with ground-truth spans. Every person, number,
// address and account is invented; company names are generic or public insurers named only as
// EMPRESA. Used to train and measure the local PII detector; never mixed with real documents.
export const FIRST_NAMES_M = ['Juan','Carlos','Luis','José','Jorge','Miguel','Pedro','Víctor','Manuel','César','Alberto','Raúl','Ricardo','Javier','Fernando','Óscar','Hugo','Walter','Edwin','Wilmer','Percy','Julio','Roberto','Daniel','Diego','Renzo','Gonzalo','Martín','Ángel','Félix','Teodoro','Segundo','Alejandro','Andrés','Eduardo','Gustavo','Héctor','Iván','Marco','Rolando'];
export const FIRST_NAMES_F = ['María','Rosa','Carmen','Ana','Luz','Elena','Gladys','Patricia','Milagros','Lucía','Sofía','Juana','Teresa','Mercedes','Esperanza','Flor','Pilar','Silvia','Diana','Karina','Rocío','Yolanda','Norma','Marleny','Erika','Jessica','Paola','Claudia','Verónica','Gabriela','Socorro','Dolores','Consuelo','Ángela','Beatriz','Cecilia','Fiorella','Katherine','Lourdes','Natalia'];
export const SURNAMES = ['Quispe','Flores','Sánchez','Rodríguez','García','Rojas','Huamán','Mamani','Vásquez','Chávez','Ramírez','Torres','Díaz','Mendoza','Castillo','Gutiérrez','Ramos','Vargas','Espinoza','Cruz','Paz','León','Rivera','Campos','Salazar','Cárdenas','Ccahuana','Condori','Apaza','Ticona','Huanca','Choque','Palomino','Tello','Villanueva','Zevallos','Aguilar','Benites','Salas','Morales','Del Castillo','De la Cruz','Del Águila','De los Santos','Pinto','Soto','Medina','Herrera','Silva','Ríos'];
export const COMPANIES = ['Seguros Andinos S.A.','Aseguradora del Pacífico Sur S.A.C.','Banco Comercial Limeño S.A.A.','Financiera Progreso del Norte S.A.','Clínica San Gabriel S.A.C.','Inversiones Valle Verde E.I.R.L.','Transportes Rápidos del Centro S.R.L.','Compañía de Seguros Horizonte S.A.','EPS Salud Integral S.A.','Caja Municipal de Ahorro Sierra Alta S.A.','Rímac Seguros y Reaseguros','Pacífico Compañía de Seguros y Reaseguros','La Positiva Seguros y Reaseguros','Mapfre Perú Compañía de Seguros y Reaseguros','Interseguro Compañía de Seguros S.A.','Protecta S.A. Compañía de Seguros','La Vista Inmobiliaria S.A.C.'];
const STREETS = ['Av. Los Próceres','Jr. Ayacucho','Calle Las Begonias','Av. Grau','Jr. Huallaga','Av. Universitaria','Calle Los Pinos','Av. Túpac Amaru','Pasaje San Martín','Av. Brasil'];
const DISTRICTS = ['San Juan de Lurigancho','Comas','Ate','Los Olivos','Surquillo','Villa El Salvador','San Martín de Porres','Cercado de Lima','Arequipa','Trujillo'];
const MONTHS = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','setiembre','octubre','noviembre','diciembre'];

export function rng(seed) {
  let s = seed >>> 0 || 1;
  return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
}
const pick = (r, list) => list[Math.floor(r() * list.length)];
const digits = (r, n) => Array.from({length: n}, () => Math.floor(r() * 10)).join('');

class Builder {
  constructor() { this.text = ''; this.spans = []; }
  add(value) { this.text += value; return this; }
  ent(type, value) { const start = this.text.length; this.text += value; this.spans.push({start, end: this.text.length, type}); return this; }
}

function person(r, b, {upper = false, gender = null} = {}) {
  const female = gender ? gender === 'F' : r() < 0.5;
  const first = pick(r, female ? FIRST_NAMES_F : FIRST_NAMES_M);
  const second = r() < 0.4 ? pick(r, female ? FIRST_NAMES_F : FIRST_NAMES_M) : null;
  const s1 = pick(r, SURNAMES), s2 = pick(r, SURNAMES);
  const fmt = v => (upper ? v.toLocaleUpperCase('es') : v);
  const nameType = 'NOMBRE_DESCONOCIDO'; // gender never inferred from the name itself
  b.ent(nameType, fmt(first));
  if (second) b.add(' ').ent(nameType, fmt(second));
  b.add(' ').ent('APELLIDO', fmt(s1)).add(' ').ent('APELLIDO', fmt(s2));
  return female;
}
const date = r => `${1 + Math.floor(r() * 28)} de ${pick(r, MONTHS)} de 202${4 + Math.floor(r() * 3)}`;
const address = r => `${pick(r, STREETS)} N.° ${100 + Math.floor(r() * 2800)}${r() < 0.4 ? `, Mz. ${String.fromCharCode(65 + Math.floor(r() * 8))} Lt. ${1 + Math.floor(r() * 30)}` : ''}, distrito de ${pick(r, DISTRICTS)}`;
const money = r => `${pick(r, ['S/ ', 'S/. ', 'US$ '])}${(100 + Math.floor(r() * 90000)).toLocaleString('en-US')}.${digits(r, 2)}`;
const card = r => `${digits(r, 4)} ${digits(r, 4)} ${digits(r, 4)} ${digits(r, 4)}`;
const expediente = r => `${String(1 + Math.floor(r() * 3999)).padStart(4, '0')}-202${4 + Math.floor(r() * 3)}/CC1`;
const ruc = r => `20${digits(r, 9)}`;
const phone = r => `9${digits(r, 8)}`;
const email = r => `${pick(r, ['contacto', 'usuario', 'reclamos', 'cliente'])}${digits(r, 3)}@${pick(r, ['correo.pe', 'mail.com', 'empresa.com.pe'])}`;

export function generateDocument(seed) {
  const r = rng(seed), b = new Builder();
  const female = r() < 0.5;
  b.add('Lima, ').add(date(r)).add('\n\nRESOLUCIÓN FINAL N.° ').ent('DOCUMENTO', `${digits(r, 4)}-2026/CC1`).add('\n\nEXPEDIENTE N.° ').ent('EXPEDIENTE', expediente(r));
  b.add('\nDENUNCIANTE: '); person(r, b, {upper: true, gender: female ? 'F' : 'M'});
  const company = pick(r, COMPANIES);
  b.add('\nDENUNCIADA: ').ent('EMPRESA', company.toLocaleUpperCase('es'));
  b.add('\nMATERIA: PROTECCIÓN AL CONSUMIDOR\n\nSUMILLA: La Comisión declara improcedente la denuncia por falta de interés para obrar.\n\n');
  b.add('ANTECEDENTES\n\n1. Mediante escrito del ').add(date(r)).add(female ? ', la señora ' : ', el señor ');
  person(r, b, {gender: female ? 'F' : 'M'});
  b.add(female ? ', identificada con DNI N.° ' : ', identificado con DNI N.° ').ent('DNI', digits(r, 8));
  b.add(', con domicilio en ').ent('DIRECCION', address(r)).add(', denunció a ').ent('EMPRESA', company);
  b.add(' (en adelante, la denunciada), con RUC N.° ').ent('RUC', ruc(r)).add(', por presunta infracción al Código de Protección y Defensa del Consumidor.\n\n');
  const variants = [
    () => { b.add('2. La denunciante indicó que contrató la póliza N.° ').ent('POLIZA', `${pick(r, ['POL', 'VEH', 'SOAT'])}-${digits(r, 7)}`).add(' y que la aseguradora rechazó el siniestro.\n\n'); },
    () => { b.add('3. Asimismo, señaló que se le cobró indebidamente el monto de ').ent('MONTO', money(r)).add(' en su tarjeta de crédito N.° ').ent('TARJETA', card(r)).add('.\n\n'); },
    () => { b.add('4. El denunciante solicitó la devolución del abono realizado en la cuenta N.° ').ent('CUENTA', `${digits(r, 3)}-${digits(r, 8)}-${digits(r, 1)}-${digits(r, 2)}`).add('.\n\n'); },
    () => { b.add('5. Para efectos de notificación, consignó el correo electrónico ').ent('CORREO', email(r)).add(' y el teléfono ').ent('TELEFONO', phone(r)).add('.\n\n'); },
    () => { b.add('6. En su descargo, el representante de la denunciada, señor '); person(r, b, {gender: 'M'}); b.add(', manifestó que actuó conforme al contrato.\n\n'); },
    () => { b.add('7. La Secretaría Técnica requirió información a la denunciada, la cual fue absuelta dentro del plazo.\n\n'); },
    () => { b.add('8. Se tiene a la vista el crédito hipotecario N.° ').ent('CREDITO', `${digits(r, 10)}`).add(' otorgado por ').ent('EMPRESA', pick(r, COMPANIES)).add('.\n\n'); },
  ];
  for (const variant of variants) if (r() < 0.75) variant();
  b.add('ANÁLISIS\n\n9. La Comisión considera que corresponde declarar improcedente la denuncia, toda vez que no se ha acreditado la relación de consumo.\n\n');
  b.add('SE RESUELVE:\n\nPRIMERO: Declarar improcedente la denuncia presentada por ');
  person(r, b, {gender: female ? 'F' : 'M'});
  b.add(' contra ').ent('EMPRESA', company).add('.\n\nCon la intervención de los señores Comisionados: ');
  person(r, b); b.add(', '); person(r, b); b.add('.\n');
  return {text: b.text, spans: b.spans};
}

export function generateCorpus(count, seed = 1) {
  return Array.from({length: count}, (_, i) => generateDocument(seed * 100003 + i));
}
