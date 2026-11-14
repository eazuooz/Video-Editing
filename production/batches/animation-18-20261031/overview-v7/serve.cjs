// Read-only delivery preview bound to the user's loopback interface.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve('C:/Users/1/Videos/YamyamCoding/animation-overview-v7');
const port = 9301;
http.createServer((request, response) => {
  if (!['GET', 'HEAD'].includes(request.method)) return response.writeHead(405).end();
  if (!["127.0.0.1:" + port, "localhost:" + port].includes(request.headers.host)) return response.writeHead(403).end();
  let pathname;
  try { pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname); }
  catch { return response.writeHead(400).end(); }
  if (pathname.endsWith('/')) pathname += 'index.html';
  const file = path.resolve(root, '.' + pathname);
  const relative = path.relative(root, file);
  if (relative.startsWith('..') || path.isAbsolute(relative) || !/\.(html|mp4|srt)$/.test(file) || !fs.existsSync(file)) {
    return response.writeHead(404).end();
  }
  const stat = fs.statSync(file);
  if (!stat.isFile()) return response.writeHead(404).end();
  let start = 0, end = stat.size - 1, status = 200;
  const headers = {'Cache-Control': 'no-store', 'Accept-Ranges': 'bytes',
    'Content-Type': file.endsWith('.mp4') ? 'video/mp4' : file.endsWith('.srt') ? 'application/x-subrip; charset=utf-8' : 'text/html; charset=utf-8'};
  if (request.headers.range) {
    const match = /^bytes=(\d+)-(\d*)$/.exec(request.headers.range);
    if (!match) return response.writeHead(416).end();
    start = Number(match[1]);
    end = match[2] ? Math.min(Number(match[2]), end) : end;
    if (start > end || start >= stat.size) return response.writeHead(416).end();
    status = 206;
    headers['Content-Range'] = `bytes ${start}-${end}/${stat.size}`;
  }
  headers['Content-Length'] = end - start + 1;
  response.writeHead(status, headers);
  if (request.method === 'HEAD') return response.end();
  fs.createReadStream(file, {start, end}).on('error', () => response.destroy()).pipe(response);
}).listen(port, '127.0.0.1', () => process.stdout.write('http://127.0.0.1:' + port + '/\n'));
