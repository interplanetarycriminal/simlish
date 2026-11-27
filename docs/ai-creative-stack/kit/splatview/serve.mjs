// Tiny static server for the viewer (ES modules and fetch do not work from file://).
// Usage: node kit/splatview/serve.mjs [root] [port]
// root defaults to the catalogue root, so ?file= can point at any PLY under it.
import { createServer } from 'node:http';
import { existsSync, readFileSync, statSync } from 'node:fs';
import { dirname, extname, relative, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const root = resolve(process.argv[2] || resolve(HERE, '..', '..'));
const port = Number(process.argv[3] || 8765);
const TYPES = { '.html': 'text/html', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.ply': 'application/octet-stream', '.glb': 'model/gltf-binary' };

createServer((req, res) => {
  const path = resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (!(path === root || path.startsWith(root + sep)) || !existsSync(path) || statSync(path).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TYPES[extname(path)] || 'application/octet-stream' });
  res.end(readFileSync(path));
}).listen(port, '127.0.0.1', () => {
  const viewer = relative(root, resolve(HERE, 'viewer.html')).split(sep).join('/');
  console.log(`serving ${root}\nopen http://127.0.0.1:${port}/${viewer}?file=<path relative to viewer.html>`);
});
