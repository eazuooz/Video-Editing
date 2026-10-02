const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const port = Number(process.env.YOUTUBE_REFRESH_PORT || 8765);
const root = path.resolve(__dirname, '..', 'output', 'youtube-library-refresh');

const contentTypes = {
  '.json': 'application/json; charset=utf-8',
  '.html': 'text/html; charset=utf-8',
  '.jpg': 'image/jpeg',
  '.png': 'image/png',
};

http.createServer((request, response) => {
  const requestedPath = decodeURIComponent(new URL(request.url, `http://127.0.0.1:${port}`).pathname);
  const relativePath = requestedPath === '/' ? 'index.html' : requestedPath.replace(/^\/+/, '');
  const filePath = path.resolve(root, relativePath);

  if (!filePath.startsWith(`${root}${path.sep}`)) {
    response.writeHead(403).end('Forbidden');
    return;
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      response.writeHead(error.code === 'ENOENT' ? 404 : 500).end('Not found');
      return;
    }

    response.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-store',
      'Content-Type': contentTypes[path.extname(filePath)] || 'application/octet-stream',
    });
    response.end(data);
  });
}).listen(port, '127.0.0.1', () => {
  process.stdout.write(`YouTube refresh review server: http://127.0.0.1:${port}\n`);
});
