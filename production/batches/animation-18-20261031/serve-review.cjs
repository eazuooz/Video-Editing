// Read-only localhost access to the current Animation research table and prototype.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const port = 9236;
const prefix = '/@fs/D:/Github/VideoEditing/';
const index = 'production/batches/animation-18-20261031/research/review-table.html';
const names = [index, 'projects/animation-assigning/production/local/grid-v1/preview/animation-grid-prototype.captioned.mp4'];
const allowed = new Map(names.map(name => [prefix + name, fs.realpathSync(path.join(root, name))]));
http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) {res.writeHead(405);return res.end();}
  const name = decodeURIComponent(new URL(req.url, 'http://127.0.0.1').pathname);
  if (name === '/') {res.writeHead(302, {Location:prefix + index});return res.end();}
  const file = allowed.get(name);
  if (!file) {res.writeHead(404);return res.end();}
  const size=fs.statSync(file).size;
  let start=0,end=size-1,status=200;
  const headers={'Content-Type':file.endsWith('.mp4')?'video/mp4':'text/html; charset=utf-8','Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
  if (req.headers.range) {
    const match=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);
    if (!match) {res.writeHead(416);return res.end();}
    start=Number(match[1]);end=match[2]?Math.min(Number(match[2]),size-1):size-1;
    if (!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>end||start>=size) {res.writeHead(416);return res.end();}
    status=206;headers['Content-Range']=`bytes ${start}-${end}/${size}`;
  }
  headers['Content-Length']=end-start+1;res.writeHead(status,headers);
  if(req.method==='HEAD')return res.end();
  fs.createReadStream(file,{start,end}).pipe(res);
}).listen(port,'127.0.0.1',()=>{
  fs.writeFileSync(path.join(__dirname,'review-server.json'),JSON.stringify({pid:process.pid,host:'127.0.0.1',port,readOnly:true,allowedFiles:names},null,2));
  process.stdout.write('Animation review table: http://127.0.0.1:9236/\n');
});
