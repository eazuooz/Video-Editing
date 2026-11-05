// Serve the math review pages and their selected media to this computer.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const hub = '/output/game-math-remaining-20261104';
const port = 9347;
const readJson = file => JSON.parse(fs.readFileSync(file, 'utf8').replace(/^\uFEFF/, ''));
const slugs = readJson(path.join(__dirname, 'batch.json')).items.map(item => item.slug);
const allowed = new Set(['index.html', 'gameplay.html', 'M25-opening-action-7s.mp4'].map(name => hub + '/' + name));
const types = {'.html':'text/html; charset=utf-8', '.mp4':'video/mp4', '.m4a':'audio/mp4', '.webm':'video/webm', '.srt':'text/plain; charset=utf-8'};

function registerMedia(file) {
  if (!file) return;
  const relative = path.relative(root, path.resolve(root, file));
  if (relative.startsWith('..') || path.isAbsolute(relative)) throw new Error('Media outside review workspace');
  allowed.add('/' + relative.split(path.sep).join('/'));
}
for (const slug of slugs.slice(1)) {
  const audit = readJson(path.join(root, 'projects', slug, 'planning/footage-audit.json'));
  for (const source of audit.sources) {
    registerMedia(source.file);
    const audio = source.audio || {};
    registerMedia(audio.separateFullOriginalAudio || audio.separateOriginalAudio || audio.recoveredOriginalAudio);
  }
}
function isDelivery(urlPath) {
  const match = /^\/output\/(game-math-[a-z0-9-]+)-render-v\d+\/([^/]+)$/.exec(urlPath);
  if (!match || !slugs.includes(match[1])) return false;
  return match[2] === 'index.html' || ['.clean.mp4','.captioned.mp4','.ko.srt','.en.srt'].some(ext => match[2] === match[1] + ext);
}
function byteRange(header, size) {
  if (header === undefined) return { start:0, end:size - 1 };
  const match = /^bytes=(\d*)-(\d*)$/.exec(header);
  if (!match || (!match[1] && !match[2])) return null;
  const start = match[1] ? Number(match[1]) : Math.max(0, size - Number(match[2]));
  const end = match[1] && match[2] ? Math.min(size - 1, Number(match[2])) : size - 1;
  return Number.isSafeInteger(start) && Number.isSafeInteger(end) && start <= end && start < size ? { start,end } : null;
}
http.createServer((req, res) => {
  if (!['GET','HEAD'].includes(req.method)) return res.writeHead(405, {Allow:'GET, HEAD'}).end();
  if (!['localhost:' + port, '127.0.0.1:' + port].includes(req.headers.host)) return res.writeHead(403).end();
  let name;
  try { name = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname); }
  catch { return res.writeHead(400).end(); }
  if (name === '/') return res.writeHead(302, {Location:hub + '/index.html'}).end();
  if (!allowed.has(name) && !isDelivery(name)) return res.writeHead(404).end();
  try {
    const file = fs.realpathSync(path.join(root, name));
    if (file.toLowerCase() !== path.resolve(root, '.' + name).toLowerCase()) return res.writeHead(403).end();
    const stat = fs.statSync(file);
    if (!stat.isFile()) return res.writeHead(404).end();
    const range = byteRange(req.headers.range, stat.size);
    if (!range) return res.writeHead(416, {'Content-Range':'bytes */' + stat.size}).end();
    const { start, end } = range;
    const headers = {'Content-Type':types[path.extname(file)] || 'application/octet-stream',
      'Content-Length':end - start + 1, 'Accept-Ranges':'bytes', 'Cache-Control':'no-cache', 'X-Content-Type-Options':'nosniff'};
    if (req.headers.range) headers['Content-Range'] = 'bytes ' + start + '-' + end + '/' + stat.size;
    res.writeHead(req.headers.range ? 206 : 200, headers);
    if (req.method === 'HEAD' || stat.size === 0) return res.end();
    const stream = fs.createReadStream(file, {start,end});
    res.on('close', () => stream.destroy());
    stream.on('error', () => res.destroy()).pipe(res);
  } catch { res.writeHead(404).end(); }
}).listen(port, '127.0.0.1');
