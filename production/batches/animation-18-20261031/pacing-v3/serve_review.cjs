// Read-only, hash-pinned delivery whitelist with byte-range playback.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),port=Number(process.argv[2]||9277);
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
 let route;try{route=new URL(req.url,'http://localhost').pathname;}catch{return res.writeHead(400).end();}
 let body;
 if(route==='/')body=fs.readFileSync(path.join(root,'output/animation-series-review/pacing-v3/index.html'));
 const match=route.match(/^\/(A\d{2})\/$/);
 if(match){const r=manifest.records.find(r=>r.id===match[1]);if(!r)return res.writeHead(404).end();body='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><style>body{background:#111914;color:#eee;font:18px/1.6 sans-serif;padding:20px}a{color:#acd9bf}video{width:100%;max-height:75vh}</style><a href="/">통합 검수 목록</a><h1>'+r.id+' '+esc(r.title)+'</h1><p>'+esc(r.description)+'</p><video controls playsinline src="captioned.mp4"></video><p>'+['captioned.mp4','clean.mp4','ko.srt','en.srt'].map((k,i)=>'<a href="'+k+'">'+['자막 영상','무자막 영상','한국어 자막','영어 자막'][i]+'</a>').join(' · ')+'</p>';}
 if(body){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-cache'});return res.end(req.method==='HEAD'?undefined:body);}
 const f=files.get(route);if(!f)return res.writeHead(404).end();const stat=fs.statSync(f.file);
 if(stat.size!==f.size||stat.mtimeMs!==f.mtime)return res.writeHead(409).end('File changed; revalidate delivery.');
 let a=0,b=f.size-1,status=200;const headers={'Content-Type':route.endsWith('.mp4')?'video/mp4':'application/x-subrip; charset=utf-8','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
 if(req.headers.range){const m=req.headers.range.match(/^bytes=(\d*)-(\d*)$/);if(!m||(!m[1]&&!m[2]))return res.writeHead(416).end();a=m[1]?Number(m[1]):Math.max(0,f.size-Number(m[2]));b=m[1]&&m[2]?Math.min(f.size-1,Number(m[2])):f.size-1;if(a>b||a>=f.size)return res.writeHead(416).end();status=206;headers['Content-Range']=`bytes ${a}-${b}/${f.size}`;}
 headers['Content-Length']=b-a+1;res.writeHead(status,headers);if(req.method==='HEAD')return res.end();fs.createReadStream(f.file,{start:a,end:b}).on('error',()=>res.destroy()).pipe(res);
});
server.listen(port,'127.0.0.1',()=>{fs.writeFileSync(path.join(__dirname,'../local/pacing-v3/review-server.json'),JSON.stringify({pid:process.pid,port,readOnly:true,hashPinned:true,episodes:manifest.records.length,startedAt:new Date().toISOString()},null,2));console.log('http://127.0.0.1:'+port+'/');});
