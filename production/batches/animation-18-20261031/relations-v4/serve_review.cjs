// Read-only, hash-pinned delivery whitelist with byte-range playback.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),port=Number(process.argv[2]||9284);
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'review-manifest.json'),'utf8'));
const files=new Map();
for(const r of manifest.records)for(const f of r.files){
 const file=path.join(root,f.path),stat=fs.statSync(file),hash=crypto.createHash('sha256'),fd=fs.openSync(file,'r'),buf=Buffer.alloc(1024*1024);let n;
 try{while((n=fs.readSync(fd,buf,0,buf.length,null)))hash.update(buf.subarray(0,n));}finally{fs.closeSync(fd);}
 if(hash.digest('hex')!==f.sha256)throw Error('Delivery hash mismatch: '+r.id+' '+f.kind);
 files.set('/'+r.id+'/'+f.kind,{file,size:stat.size,mtime:stat.mtimeMs});
}
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
const server=http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method))return res.writeHead(405).end();
 if(!['127.0.0.1:'+port,'localhost:'+port].includes(req.headers.host))return res.writeHead(403).end();
 let route,requestUrl;try{requestUrl=new URL(req.url,'http://localhost');route=requestUrl.pathname;}catch{return res.writeHead(400).end();}
 let body;
 if(route==='/')body=fs.readFileSync(path.join(__dirname,'review.html'));
 const match=route.match(/^\/(A\d{2})\/$/);
 if(match){const index=manifest.records.findIndex(r=>r.id===match[1]),r=manifest.records[index];if(!r)return res.writeHead(404).end();const seek=Number(requestUrl.searchParams.get('t')||0),start=Number.isFinite(seek)&&seek>=0&&seek<r.durationSeconds?seek:0,mapAt=(r.insertion.pictureFrame/60).toFixed(3);const nav=[index>0?'<a href="/'+manifest.records[index-1].id+'/">← 이전 편</a>':'','<a href="/">통합 검수 목록</a>',index+1<manifest.records.length?'<a href="/'+manifest.records[index+1].id+'/">다음 편 →</a>':''].filter(Boolean).join(' · ');body='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#111914;color:#eee;font:18px/1.6 sans-serif;padding:20px}h1{color:#f2d787;font-size:28px}a{color:#acd9bf}video{width:100%;max-height:75vh}nav{margin:12px 0}</style><nav>'+nav+'</nav><h1>'+r.id+' '+esc(r.title)+'</h1><p>'+esc(r.description)+'</p><p><a href="?t='+mapAt+'">관계도부터 보기</a> · <a href="?t=0">처음부터 보기</a></p><video controls playsinline preload="metadata" src="captioned.mp4'+(start?'#t='+start:'')+'"></video><p>'+['captioned.mp4','clean.mp4','ko.srt','en.srt'].map((k,i)=>'<a href="'+k+'">'+['자막 영상','무자막 영상','한국어 자막','영어 자막'][i]+'</a>').join(' · ')+'</p><nav>'+nav+'</nav>';}
 if(body){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache'});return res.end(req.method==='HEAD'?undefined:body);}
 const f=files.get(route);if(!f)return res.writeHead(404).end();const stat=fs.statSync(f.file);
 if(stat.size!==f.size||stat.mtimeMs!==f.mtime)return res.writeHead(409).end('File changed; revalidate delivery.');
 let a=0,b=f.size-1,status=200;const headers={'Content-Type':route.endsWith('.mp4')?'video/mp4':'application/x-subrip; charset=utf-8','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
 if(req.headers.range){const m=req.headers.range.match(/^bytes=(\d*)-(\d*)$/);if(!m||(!m[1]&&!m[2]))return res.writeHead(416).end();a=m[1]?Number(m[1]):Math.max(0,f.size-Number(m[2]));b=m[1]&&m[2]?Math.min(f.size-1,Number(m[2])):f.size-1;if(a>b||a>=f.size)return res.writeHead(416).end();status=206;headers['Content-Range']=`bytes ${a}-${b}/${f.size}`;}
 headers['Content-Length']=b-a+1;res.writeHead(status,headers);if(req.method==='HEAD')return res.end();fs.createReadStream(f.file,{start:a,end:b}).on('error',()=>res.destroy()).pipe(res);
});
server.listen(port,'127.0.0.1',()=>{fs.writeFileSync(path.join(__dirname,'local/review-server.json'),JSON.stringify({pid:process.pid,port,readOnly:true,hashPinned:true,episodes:manifest.records.length,startedAt:new Date().toISOString()},null,2));console.log('http://127.0.0.1:'+port+'/');});
