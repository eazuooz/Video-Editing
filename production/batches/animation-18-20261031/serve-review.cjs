// Read-only loopback access. Deliveries enter the whitelist only after their
// complete four-file manifests and actual bytes validate at server startup.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const args = process.argv.slice(2);
if (args.length && !(args.length === 2 && args[0] === '--port')) throw new Error('Usage: node serve-review.cjs [--port 9237]');
const port = args.length ? Number(args[1]) : 9237;
if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error('Invalid loopback port');
const prefix = '/@fs/D:/Github/VideoEditing/';
const index = 'production/batches/animation-18-20261031/research/review-table.html';
const names = [index, 'projects/animation-assigning/production/local/grid-v1/preview/animation-grid-prototype.captioned.mp4'];
const allowed = new Map();
const deliveries = [], rejected = [];
const batch = JSON.parse(fs.readFileSync(path.join(__dirname,'batch.json'),'utf8').replace(/^\uFEFF/,''));
const withinRoot = file => {
  const real = fs.realpathSync(file), rel = path.relative(root, real);
  if (rel.startsWith('..') || path.isAbsolute(rel)) throw new Error('Path outside workspace');
  return real;
};
function digest(file) {
  const hash=crypto.createHash('sha256'), buffer=Buffer.allocUnsafe(4*1024*1024), fd=fs.openSync(file,'r');
  try {let length;while ((length=fs.readSync(fd,buffer,0,buffer.length,null))>0) hash.update(buffer.subarray(0,length));}
  finally {fs.closeSync(fd);}
  return hash.digest('hex');
}
function register(file, pinned=false) {
  const real=withinRoot(file), stat=fs.statSync(real), name=path.relative(root,real).replaceAll('\\','/');
  if (!stat.isFile()) throw new Error('Not a regular file');
  allowed.set(prefix+name,{file:real,size:stat.size,mtimeMs:stat.mtimeMs,pinned});
  return name;
}
for (const name of names) if(fs.existsSync(path.join(root,name))) register(path.join(root,name));
function addDelivery(manifestFile) {
  const directory=path.dirname(withinRoot(manifestFile));
  const m=JSON.parse(fs.readFileSync(manifestFile,'utf8').replace(/^\uFEFF/,''));
  if (!batch.episodeIds.includes(m.episode) || !/^[a-z0-9-]+$/.test(m.slug)) throw new Error('Outside this finite batch');
  if (m.status!=='collected-verified-master-pair-user-review-pending' || m.verification?.structuralFinalPair!=='pass') throw new Error('Verified pair delivery required');
  if (m.format?.width!==1920 || m.format?.height!==1080 || m.format?.fps!==60) throw new Error('Expected FHD60');
  if (path.resolve(root,m.directory)!==directory) throw new Error('Manifest directory mismatch');
  const suffixes=['captioned.mp4','clean.mp4','ko.srt','en.srt'];
  if (m.files?.length!==4 || new Set(m.files.map(x=>x.role)).size!==4) throw new Error('Expected four distinct outputs');
  const verified=[];
  for (const suffix of suffixes) {
    const item=m.files.find(x=>x.role===suffix);
    if (!item || item.name!==`${m.slug}.${suffix}`) throw new Error('Unexpected output filename');
    const file=withinRoot(path.join(directory,item.name));
    if (path.dirname(file)!==directory || fs.statSync(file).size!==item.bytes || digest(file)!==item.sha256) throw new Error('Delivery file hash/size mismatch');
    verified.push(file);
  }
  if (m.files.find(x=>x.role==='captioned.mp4').sha256!==m.captionedMasterSha256) throw new Error('Captioned master hash mismatch');
  const page=m.metadataArtifacts?.find(x=>x.name==='index.html'), pageFile=path.join(directory,'index.html');
  if (!page || fs.statSync(pageFile).size!==page.bytes || digest(pageFile)!==page.sha256) throw new Error('Index is not the manifest-bound version');
  const readme=m.metadataArtifacts?.find(x=>x.name==='README.md'), readmeFile=path.join(directory,'README.md');
  if (!readme || fs.statSync(readmeFile).size!==readme.bytes || digest(readmeFile)!==readme.sha256) throw new Error('README is not the manifest-bound version');
  verified.push(pageFile,readmeFile,manifestFile);
  const exposed=verified.map(file=>register(file,true));
  deliveries.push({episode:m.episode,slug:m.slug,captionedMasterSha256:m.captionedMasterSha256,manifestSha256:digest(manifestFile),allowedFiles:exposed});
}
for (const project of fs.readdirSync(path.join(root,'projects'),{withFileTypes:true}).filter(x=>x.isDirectory())) {
  const local=path.join(root,'projects',project.name,'production','local');
  if (!fs.existsSync(local)) continue;
  for(const revision of fs.readdirSync(local,{withFileTypes:true}).filter(x=>x.isDirectory())) {
    const manifest=path.join(local,revision.name,'delivery','output',project.name,'delivery-manifest.json');
    if(!fs.existsSync(manifest)) continue;
    // Ignore unrelated projects before checking their media or recording errors.
    try {
      const header=JSON.parse(fs.readFileSync(manifest,'utf8').replace(/^\uFEFF/,''));
      if(!batch.episodeIds.includes(header.episode)) continue;
      addDelivery(manifest);
    } catch(error) {rejected.push({manifest:path.relative(root,manifest).replaceAll('\\','/'),reason:error.message});}
  }
}
const mime={'.mp4':'video/mp4','.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8','.srt':'application/x-subrip; charset=utf-8','.md':'text/plain; charset=utf-8'};
const server=http.createServer((req, res) => {
  if (!['GET', 'HEAD'].includes(req.method)) {res.writeHead(405,{Allow:'GET, HEAD'});return res.end();}
  let name;
  try {name=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);} catch {res.writeHead(400);return res.end();}
  if (name === '/') {res.writeHead(302, {Location:prefix + index});return res.end();}
  const entry = allowed.get(name);
  if (!entry) {res.writeHead(404);return res.end();}
  const file=entry.file;
  let stat;
  try {stat=fs.statSync(file);} catch {res.writeHead(404);return res.end();}
  if(entry.pinned && (stat.size!==entry.size || stat.mtimeMs!==entry.mtimeMs)) {res.writeHead(409);return res.end('Delivery changed; revalidate server whitelist.');}
  const size=stat.size;
  let start=0,end=size-1,status=200;
  const headers={'Content-Type':mime[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
  if (req.headers.range) {
    const match=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
    if (!match || (!match[1]&&!match[2])) {res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end();}
    if(!match[1]) {const suffix=Number(match[2]);start=Math.max(0,size-suffix);}
    else {start=Number(match[1]);end=match[2]?Math.min(Number(match[2]),size-1):size-1;}
    if (!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>end||start>=size) {res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end();}
    status=206;headers['Content-Range']=`bytes ${start}-${end}/${size}`;
  }
  headers['Content-Length']=end-start+1;res.writeHead(status,headers);
  if(req.method==='HEAD')return res.end();
  const stream=fs.createReadStream(file,{start,end});stream.on('error',()=>res.destroy());stream.pipe(res);
});
server.on('error',error=>{process.stderr.write(error.message+'\n');process.exitCode=1;});
server.listen(port,'127.0.0.1',()=>{
  fs.writeFileSync(path.join(__dirname,`review-server-${port}.json`),JSON.stringify({pid:process.pid,host:'127.0.0.1',port,readOnly:true,startedAt:new Date().toISOString(),allowedFiles:[...allowed.keys()],deliveries,rejected,methodWhitelist:['GET','HEAD'],deliveryRegistration:'startup hash validation; no auto-discovery of incomplete future outputs'},null,2));
  process.stdout.write(`Animation review table: http://127.0.0.1:${port}/\n`);
});
