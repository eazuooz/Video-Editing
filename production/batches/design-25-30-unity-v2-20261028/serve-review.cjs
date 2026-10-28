// Loopback-only review of this finite batch; no repository directory browsing.
const http=require('node:http');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const batch='design-25-30-unity-v2-20261028';
const storage=path.resolve('C:/Users/1/.codex/video-production',batch);
const slugs=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time'];
const index='output/game-design-25-30-unity-v2-20261028/index.html';
const allowed=new Set([index]);
for(const s of slugs)for(const f of ['index.html',`${s}.captioned.mp4`,`${s}.clean.mp4`,`${s}.ko.srt`,`${s}.en.srt`])
  allowed.add(`projects/${s}/production/local/unity-visual-v2/delivery/output/${s}/${f}`);
const prefix='/@fs/D:/Github/VideoEditing/';
const server=http.createServer((req,res)=>{
  try{
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);return res.end();}
    const pathname=decodeURIComponent(new URL(req.url,'http://127.0.0.1:9232').pathname);
    if(pathname==='/'){res.writeHead(302,{Location:prefix+index});return res.end();}
    if(!pathname.startsWith(prefix)){res.writeHead(404);return res.end();}
    const rel=pathname.slice(prefix.length);
    if(!allowed.has(rel)){res.writeHead(404);return res.end();}
    const file=path.resolve(root,rel);
    const real=fs.realpathSync(file);
    if(!real.toLowerCase().startsWith((storage+path.sep).toLowerCase()))throw Error('Storage boundary');
    const stat=fs.statSync(real);let start=0,end=stat.size-1,status=200;
    const headers={'Content-Type':real.endsWith('.mp4')?'video/mp4':real.endsWith('.srt')?'text/plain; charset=utf-8':'text/html; charset=utf-8','Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
    if(req.headers.range){
      const match=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if(!match||(!match[1]&&!match[2])){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`});return res.end();}
      if(match[1]){start=Number(match[1]);if(match[2])end=Number(match[2]);}
      else start=Math.max(0,stat.size-Number(match[2]));
      if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start<0||start>end||start>=stat.size){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`});return res.end();}
      end=Math.min(end,stat.size-1);
      status=206;headers['Content-Range']=`bytes ${start}-${end}/${stat.size}`;
    }
    headers['Content-Length']=end-start+1;res.writeHead(status,headers);
    if(req.method==='HEAD')return res.end();
    fs.createReadStream(real,{start,end}).on('error',()=>res.destroy()).pipe(res);
  }catch(error){if(!res.headersSent)res.writeHead(error.code==='ENOENT'?404:500);res.end();}
});
server.listen(9232,'127.0.0.1',()=>{
  fs.writeFileSync(path.join(storage,'review-server.json'),JSON.stringify({pid:process.pid,host:'127.0.0.1',port:9232,batch,startedAt:new Date().toISOString(),readOnly:true,allowedFiles:allowed.size},null,2));
  process.stdout.write('Finite batch local review server ready\n');
});
