// Read-only batch review. Only complete deliveries with a matching receipt may be opened.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const batch = JSON.parse(fs.readFileSync(path.join(__dirname, 'batch.json'), 'utf8'));
const worklist = JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-worklist.json'), 'utf8').replace(/^\uFEFF/, ''));
const history = {A01:'unreal-kit-v2',A02:'fighters-v4-kula-lili',A03:'grid-v1'};
const episodes = batch.episodes.map(episode => ({
  id:episode.id, title:episode.titleKo,
  slug:worklist.rows.find(row => row.id === episode.id).slug,
  revision:history[episode.id] || 'series-v1',
}));
const cache = new Map();
const relative = file => path.relative(root,file).replaceAll('\\','/');
function digest(file) {
  const stat=fs.statSync(file),key=file+'|'+stat.size+'|'+stat.mtimeMs;
  if(cache.has(key))return cache.get(key);
  const h=crypto.createHash('sha256'),buf=Buffer.allocUnsafe(1024*1024),fd=fs.openSync(file,'r');
  try {let n;while((n=fs.readSync(fd,buf,0,buf.length,null)))h.update(buf.subarray(0,n));}
  finally {fs.closeSync(fd);}
  const value=h.digest('hex');cache.set(key,value);return value;
}
function delivery(e) {
  const base=path.join(root,'projects',e.slug,'production'), dir=path.join(base,'local',e.revision,'delivery','output',e.slug);
  const ledger=path.join(base,e.revision,'checkpoint.json');
  if(!fs.existsSync(ledger))return;
  const j=JSON.parse(fs.readFileSync(ledger,'utf8').replace(/^\uFEFF/,''));
  const expected=j.captionedMasterSha256 || j.masterSha256;
  const master=path.join(dir,e.slug+'.captioned.mp4');
  if(!expected || !['captioned.mp4','clean.mp4','ko.srt','en.srt'].every(s=>fs.existsSync(path.join(dir,e.slug+'.'+s))))return;
  if(digest(master)!==expected)return;
  return dir;
}
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const port=Number(process.argv[2]||9248);
const server=http.createServer((req,res)=>{
  if(!['GET','HEAD'].includes(req.method))return res.writeHead(405).end();
  if(!['127.0.0.1:'+port,'localhost:'+port].includes(req.headers.host))return res.writeHead(403).end();
  let name;try{name=new URL(req.url,'http://localhost').pathname;}catch{return res.writeHead(400).end();}
  if(name==='/'){
    const rows=episodes.map(e=>{
      const hit=delivery(e);
      return '<tr><th>'+e.id+'</th><td>'+esc(e.title)+'</td><td>'+(hit?'<a href="/'+e.id+'/captioned.mp4">전체 영상</a> · <a href="/'+e.id+'/ko.srt">한글</a> · <a href="/'+e.id+'/en.srt">영문</a>':'제작 준비')+'</td></tr>';
    });
    const body='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name=viewport content="width=device-width"><title>게임 애니메이션 검수</title><style>body{margin:40px auto;max-width:960px;padding:0 18px;font:17px/1.6 sans-serif;color:#13231d}table{border-collapse:collapse;width:100%}th,td{padding:10px;text-align:left;border-bottom:1px solid #cfdad2}a{color:#075746}</style><h1>게임 애니메이션 검수</h1><table><thead><tr><th>편</th><th>제목</th><th>검수본</th></tr></thead><tbody>'+rows.join('')+'</tbody></table></html>';
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache'});return res.end(req.method==='HEAD'?undefined:body);
  }
  const m=name.match(/^\/(A\d{2})\/(captioned\.mp4|clean\.mp4|ko\.srt|en\.srt)$/);
  if(!m)return res.writeHead(404).end();const e=episodes.find(v=>v.id===m[1]);const dir=e&&delivery(e);
  if(!dir)return res.writeHead(404).end();
  const f=path.join(dir,e.slug+'.'+m[2]);if(!relative(fs.realpathSync(f)).startsWith('projects/'+e.slug+'/production/local/'))return res.writeHead(403).end();
  const size=fs.statSync(f).size;let a=0,b=size-1,status=200;const headers={'Content-Type':m[2].endsWith('.mp4')?'video/mp4':'application/x-subrip; charset=utf-8','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
  if(req.headers.range){const range=req.headers.range.match(/^bytes=(\d*)-(\d*)$/);if(!range||(!range[1]&&!range[2]))return res.writeHead(416).end();a=range[1]?Number(range[1]):Math.max(0,size-Number(range[2]));b=range[1]&&range[2]?Math.min(size-1,Number(range[2])):size-1;if(a>b||a>=size)return res.writeHead(416).end();status=206;headers['Content-Range']='bytes '+a+'-'+b+'/'+size;}
  headers['Content-Length']=b-a+1;res.writeHead(status,headers);if(req.method==='HEAD')return res.end();fs.createReadStream(f,{start:a,end:b}).on('error',()=>res.destroy()).pipe(res);
});
server.listen(port,'127.0.0.1');
