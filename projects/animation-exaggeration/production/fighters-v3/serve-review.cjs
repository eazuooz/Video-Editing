// Read-only loopback playback of this manifest-bound delivery only.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),local=path.resolve(__dirname,'../local/fighters-v3');
const dir=path.join(local,'delivery/output/animation-exaggeration'),manifestFile=path.join(dir,'delivery-manifest.json');
const manifest=JSON.parse(fs.readFileSync(manifestFile,'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
if(manifest.revision!=='fighters-v3'||manifest.verification.structuralFinalPair!=='pass')throw Error('Verified revision required');
const allowed=new Map(),prefix='/@fs/D:/Github/VideoEditing/';
for(const item of manifest.files){
 const file=path.resolve(dir,item.name);
 if(path.dirname(file)!==dir||fs.statSync(file).size!==item.bytes||sha(file)!==item.sha256)throw Error('Delivery mismatch');
}
for(const name of [...manifest.files.map(x=>x.name),'index.html','sources.txt','delivery-manifest.json']){
 const file=path.join(dir,name),stat=fs.statSync(file);
 allowed.set(prefix+path.relative(root,file).replaceAll('\\','/'),{file,size:stat.size,mtime:stat.mtimeMs});
}
const index=prefix+path.relative(root,path.join(dir,'index.html')).replaceAll('\\','/');
const mime={'.mp4':'video/mp4','.html':'text/html; charset=utf-8','.json':'application/json; charset=utf-8','.srt':'application/x-subrip; charset=utf-8','.txt':'text/plain; charset=utf-8'};
const server=http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);return res.end();}
 let name;try{name=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);}catch{res.writeHead(400);return res.end();}
 if(name==='/'){res.writeHead(302,{Location:index});return res.end();}
 const entry=allowed.get(name);if(!entry){res.writeHead(404);return res.end();}
 const stat=fs.statSync(entry.file);if(stat.size!==entry.size||stat.mtimeMs!==entry.mtime){res.writeHead(409);return res.end();}
 let start=0,end=entry.size-1,status=200;
 const headers={'Content-Type':mime[path.extname(entry.file)],'Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
 if(req.headers.range){
  const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
  if(!m||(!m[1]&&!m[2])){res.writeHead(416);return res.end();}
  if(!m[1])start=Math.max(0,entry.size-Number(m[2]));else{start=Number(m[1]);if(m[2])end=Math.min(Number(m[2]),end);}
  if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>end||start>=entry.size){res.writeHead(416,{'Content-Range':`bytes */${entry.size}`});return res.end();}
  status=206;headers['Content-Range']=`bytes ${start}-${end}/${entry.size}`;
 }
 headers['Content-Length']=end-start+1;res.writeHead(status,headers);
 if(req.method==='HEAD')return res.end();
 const stream=fs.createReadStream(entry.file,{start,end});stream.on('error',()=>res.destroy());stream.pipe(res);
});
server.listen(9238,'127.0.0.1',()=>{
 fs.writeFileSync(path.join(local,'review-server.json'),JSON.stringify({pid:process.pid,port:9238,readOnly:true,captionedMasterSha256:manifest.captionedMasterSha256,files:[...allowed.keys()],startedAt:new Date().toISOString()},null,2));
 console.log('A02 local review: http://127.0.0.1:9238/');
});
