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
const css='body{margin:32px auto;max-width:1000px;padding:0 18px;font:17px/1.6 system-ui,sans-serif;color:#13231d}table{border-collapse:collapse;width:100%}th,td{padding:10px 8px;text-align:left;border-bottom:1px solid #cfdad2}th{white-space:nowrap}a{color:#075746}h1{line-height:1.3}video{width:100%;max-height:65vh;background:#111}small{color:#53645b;display:block} @media(max-width:540px){body{margin:18px auto;font-size:15px}th,td{padding:7px 4px}}';
function clock(seconds) {
  const n = Math.round(seconds);
  return Math.floor(n / 60) + ':' + String(n % 60).padStart(2, '0');
}
function writeFinalIndex() {
  const output = path.join(root, 'output', 'animation-series-review');
  const {execFileSync} = require('node:child_process');
  const records = episodes.map(e => {
    const dir = delivery(e);
    if (!dir) throw new Error('Missing verified master: ' + e.id);
    const url = filename => path.relative(output, path.join(dir, filename))
      .split(path.sep).map(part => encodeURIComponent(part)).join('/');
    const movie = e.slug + '.captioned.mp4';
    const duration = Number(execFileSync('ffprobe', ['-v','error','-show_entries','format=duration',
      '-of','default=nw=1:nk=1',path.join(dir,movie)], {encoding:'utf8'}).trim());
    if (!(duration > 0) || !fs.existsSync(path.join(dir,'index.html'))) throw new Error('Invalid delivery: ' + e.id);
    return {id:e.id,title:e.title,seconds:duration,movie:url(movie),files:url('index.html')};
  });
  const table = records.map(e => '<tr id="'+e.id+'"><th>'+e.id+'</th><td><a class="play" href="'+e.movie+
    '">'+esc(e.title)+'</a></td><td>'+clock(e.seconds)+'</td><td><a href="'+e.files+'">파일 모음</a></td></tr>').join('');
  const total = records.reduce((sum, e) => sum + e.seconds, 0);
  const fresh = records.filter(e => Number(e.id.slice(1)) >= 8).reduce((sum,e) => sum + e.seconds, 0);
  const body = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+
    '<title>얌얌코딩 게임 애니메이션 검수</title><style>'+css+'tr[aria-current=true]{background:#eaf3ec}</style>'+
    '<h1>게임 애니메이션 통합 검수</h1><p>전체 18편 '+clock(total)+' · 이번 검수 A08–A18 '+clock(fresh)+'</p>'+
    '<h2 id="now"></h2><video id="preview" controls preload="metadata" playsinline></video>'+
    '<table><thead><tr><th>편</th><th>제목</th><th>길이</th><th>영상·자막</th></tr></thead><tbody>'+table+'</tbody></table>'+
    '<script>const rows=[...document.querySelectorAll("tbody tr")],player=document.querySelector("video"),heading=document.getElementById("now");let current;'+
    'function select(i,play){if(i<0||i>=rows.length)return; if(current!==undefined)rows[current].removeAttribute("aria-current");'+
    'current=i;const row=rows[i],link=row.querySelector(".play");row.setAttribute("aria-current","true");heading.textContent=row.id+" · "+link.textContent;'+
    'player.src=link.href;if(play)player.play().catch(()=>{});}'+
    'if(location.protocol==="http:"||location.protocol==="https:")for(const row of rows){row.querySelector(".play").href="/"+row.id+"/captioned.mp4";row.lastElementChild.firstElementChild.href="/"+row.id+"/";}'+
    'rows.forEach((r,i)=>r.querySelector(".play").onclick=e=>{e.preventDefault();select(i,true);});'+
    'player.addEventListener("ended",()=>select(current+1,true));select(rows.findIndex(r=>r.id==="A08"),false);</script></html>';
  fs.mkdirSync(output, {recursive:true});
  fs.writeFileSync(path.join(output,'index.html'),body,'utf8');
  console.log(JSON.stringify({directory:output,episodes:records.length,totalSeconds:total,newSeconds:fresh}));
}
if (process.argv[2] === '--write-final-index') {
  writeFinalIndex();
  process.exit(0);
}
function progress(e) {
  const prod=path.join(root,'projects',e.slug,'production');
  const local=path.join(prod,'local',e.revision);
  if(fs.existsSync(path.join(local,'voice','narration.asr-review.json')))return '영상 편집·검사 중';
  if(fs.existsSync(path.join(local,'voice','chunks')))return '음성 제작 중';
  if(fs.existsSync(path.join(prod,e.revision,'production-binding.json')))return '대본·시연 준비 완료';
  return '자료 준비 중';
}
const port=Number(process.argv[2]||9248);
const server=http.createServer((req,res)=>{
  if(!['GET','HEAD'].includes(req.method))return res.writeHead(405).end();
  if(!['127.0.0.1:'+port,'localhost:'+port].includes(req.headers.host))return res.writeHead(403).end();
  let name;try{name=new URL(req.url,'http://localhost').pathname;}catch{return res.writeHead(400).end();}
  if(name==='/'){
    const finalIndex=path.join(root,'output','animation-series-review','index.html');
    if(fs.existsSync(finalIndex) && episodes.every(e=>delivery(e))) {
      res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache'});
      if(req.method==='HEAD')return res.end();
      return fs.createReadStream(finalIndex).on('error',()=>res.destroy()).pipe(res);
    }
    let ready=0;
    const rows=episodes.map(e=>{
      const hit=delivery(e);
      if(hit)ready++;
      return '<tr><th>'+e.id+'</th><td>'+esc(e.title)+'</td><td>'+(hit?'<a href="/'+e.id+'/captioned.mp4">전체 영상</a> · <a href="/'+e.id+'/">파일 모음</a>':progress(e))+'</td></tr>';
    });
    const body='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name=viewport content="width=device-width"><title>게임 애니메이션 검수</title><style>'+css+'</style><h1>게임 애니메이션 검수</h1><p>전체 '+episodes.length+'편 중 '+ready+'편 재생 가능</p><table><thead><tr><th>편</th><th>제목</th><th>검수본</th></tr></thead><tbody>'+rows.join('')+'</tbody></table></html>';
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache'});return res.end(req.method==='HEAD'?undefined:body);
  }
  const folder=name.match(/^\/(A\d{2})\/$/);
  if(folder){
    const e=episodes.find(entry=>entry.id===folder[1]);
    if(!e||!delivery(e))return res.writeHead(404).end();
    const body='<!doctype html><html lang="ko"><meta charset=utf-8><meta name=viewport content="width=device-width"><title>'+esc(e.title)+'</title><style>'+css+'</style><a href="/">전체 목록</a><h1>'+e.id+' '+esc(e.title)+'</h1><video controls preload="metadata" playsinline src="captioned.mp4"></video><p><a href="captioned.mp4">자막 포함 영상</a> · <a href="clean.mp4">자막 없는 영상</a></p><p><a href="ko.srt" download>한국어 자막</a> · <a href="en.srt" download>영어 자막</a></p></html>';
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
