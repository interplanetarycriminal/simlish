// Turn every number in a flat record into the hex of its IEEE-754 float64 bits, so equality is bitwise.
const view = new DataView(new ArrayBuffer(8));
export function hex64(n) {
  view.setFloat64(0, n);
  return view.getBigUint64(0).toString(16).padStart(16, '0');
}
export function bitsOf(record) {
  return Object.fromEntries(Object.entries(record).map(([k, v]) => [k, typeof v === 'number' ? hex64(v) : v]));
}
