const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = 'C:/Users/1/Videos/YamyamCoding/design-specifics-18-review';
const port = Number(process.argv[2] ?? 9298);
const contentType = {html: 'text/html; charset=utf-8', mp4: 'video/mp4', srt: 'application/x-subrip; charset=utf-8'};

function locate(url) {
  if (url === '/' || url === '/index.html') return path.join(root, 'index.html');
  const match = /^\/(DS(?:0[1-9]|1[0-8]))\/(.*)$/.exec(url);
  if (!match) return null;
  const [, episode, requested] = match;
  const directory = path.join(root, episode);
  const receipt = path.join(directory, 'delivery.json');
  if (!fs.existsSync(receipt)) return null;
  const delivery = JSON.parse(fs.readFileSync(receipt, 'utf8'));
  if (delivery.episode !== episode || delivery.stage !== 'local-final-review-ready') return null;
  if (!requested || requested === 'index.html') return path.join(directory, 'index.html');
  const allowed = ['captioned.mp4', 'clean.mp4', 'ko.srt', 'en.srt'].map(kind => `${episode}.${kind}`);
  if (!allowed.includes(requested)) return null;
  return path.join(directory, requested);
}

function byteRange(value, size) {
  if (!value) return {start: 0, end: size - 1, status: 200};
  const match = /^bytes=(\d*)-(\d*)$/.exec(value);
  if (!match || (!match[1] && !match[2])) return null;
  const [, left, right] = match;
  const start = left ? Number(left) : Math.max(0, size - Number(right));
  const end = left && right ? Math.min(size - 1, Number(right)) : size - 1;
  return start <= end && start < size ? {start, end, status: 206} : null;
}

http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) return res.writeHead(405).end();
  if (![ `127.0.0.1:${port}`, `localhost:${port}` ].includes(req.headers.host)) return res.writeHead(403).end();
  try {
    const file = locate(new URL(req.url, `http://127.0.0.1:${port}`).pathname);
    if (!file || !fs.existsSync(file)) return res.writeHead(404).end();
    const {size} = fs.statSync(file);
    const bytes = byteRange(req.headers.range, size);
    if (!bytes) return res.writeHead(416, {'Content-Range': `bytes */${size}`}).end();
    const {start, end, status} = bytes;
    const headers = {'Content-Type': contentType[path.extname(file).slice(1)], 'Accept-Ranges': 'bytes',
      'Cache-Control': 'no-store', 'Content-Length': end - start + 1};
    if (status === 206) headers['Content-Range'] = `bytes ${start}-${end}/${size}`;
    res.writeHead(status, headers);
    if (req.method === 'HEAD') return res.end();
    fs.createReadStream(file, {start, end}).on('error', () => res.destroy()).pipe(res);
  } catch {
    if (res.headersSent) return res.destroy();
    res.writeHead(400).end();
  }
}).listen(port, '127.0.0.1', () => console.log(`http://127.0.0.1:${port}/`));
