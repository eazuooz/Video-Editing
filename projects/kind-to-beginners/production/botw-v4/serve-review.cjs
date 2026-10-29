// Serve only this D29 BOTW revision's five review files and isolated index.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../../..');
const batch = 'kind-to-beginners-botw-v4';
const deliveryOutput = 'projects/kind-to-beginners/production/local/botw-v4/delivery/output/';
const folder = deliveryOutput + 'kind-to-beginners/';
const index = folder + 'index.html';
const parentIndex = deliveryOutput + 'index.html';
const allowed = new Map();
for (const name of ['index.html','kind-to-beginners.captioned.mp4','kind-to-beginners.clean.mp4','kind-to-beginners.ko.srt','kind-to-beginners.en.srt']) {
  const relative = folder + name;
  allowed.set(relative, path.resolve(root, relative));
}
// collect-video-output.cjs writes this exact parent index and links to it as
// ../index.html. Do not expose the repository-wide output index or directories.
allowed.set(parentIndex, path.resolve(root, parentIndex));
const prefix = '/@fs/D:/Github/VideoEditing/';
const port = 9235;
const server = http.createServer((req, res) => {
  try {
    if (!['GET', 'HEAD'].includes(req.method)) { res.writeHead(405); return res.end(); }
    const pathname = decodeURIComponent(new URL(req.url, `http://127.0.0.1:${port}`).pathname);
    if (pathname === '/') { res.writeHead(302, {Location: prefix + index}); return res.end(); }
    if (!pathname.startsWith(prefix)) { res.writeHead(404); return res.end(); }
    const relative = pathname.slice(prefix.length);
    const expected = allowed.get(relative);
    if (!expected) { res.writeHead(404); return res.end(); }
    // During a first collection the parent index can be written last. Its link
    // still resolves safely to this revision's page until that file exists.
    if (relative === parentIndex && !fs.existsSync(expected)) {
      res.writeHead(302, {Location: prefix + index}); return res.end();
    }
    const real = fs.realpathSync(path.resolve(root, relative));
    if (real.toLowerCase() !== expected.toLowerCase()) throw Error('Unexpected file destination');
    const stat = fs.statSync(real);
    if (!stat.isFile()) { res.writeHead(404); return res.end(); }
    let start = 0, end = stat.size - 1, status = 200;
    const headers = {'Content-Type': real.endsWith('.mp4') ? 'video/mp4' : real.endsWith('.srt') ? 'text/plain; charset=utf-8' : 'text/html; charset=utf-8',
      'Accept-Ranges': 'bytes', 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff'};
    if (req.headers.range) {
      const match = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if (!match || (!match[1] && !match[2])) { res.writeHead(416, {'Content-Range': `bytes */${stat.size}`}); return res.end(); }
      if (match[1]) { start = Number(match[1]); if (match[2]) end = Number(match[2]); }
      else start = Math.max(0, stat.size - Number(match[2]));
      if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || start > end || start >= stat.size) {
        res.writeHead(416, {'Content-Range': `bytes */${stat.size}`}); return res.end();
      }
      end = Math.min(end, stat.size - 1);
      status = 206; headers['Content-Range'] = `bytes ${start}-${end}/${stat.size}`;
    }
    headers['Content-Length'] = end - start + 1;
    res.writeHead(status, headers);
    if (req.method === 'HEAD') return res.end();
    fs.createReadStream(real, {start, end}).on('error', () => res.destroy()).pipe(res);
  } catch (error) {
    if (!res.headersSent) res.writeHead(error instanceof URIError ? 400 : error.code === 'ENOENT' ? 404 : 500);
    res.end();
  }
});
server.listen(port, '127.0.0.1', () => {
  fs.writeFileSync(path.join(__dirname, 'review-server.json'), JSON.stringify({pid: process.pid, host: '127.0.0.1', port,
    batch, startedAt: new Date().toISOString(), readOnly: true, allowedFiles: allowed.size}, null, 2));
  process.stdout.write('Selected revision review server ready\n');
});
