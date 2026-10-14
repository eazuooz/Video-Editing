// Local read-only range serving for current review. No renderer, upload or mutation endpoints.
const http=require('node:http'), fs=require('node:fs'), path=require('node:path');
const root=path.resolve(__dirname,'../../..'), allowed=path.join(__dirname,'local');
const server=http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
 let file;
 try{
  let raw=decodeURIComponent(new URL(req.url,'http://127.0.0.1:9270').pathname);
  if(!raw.startsWith('/@fs/'))throw Error('review path required');
  raw=raw.slice(5); file=path.resolve(raw);
  if(!file.toLowerCase().startsWith(allowed.toLowerCase()+path.sep)||!['.html','.mp4','.png'].includes(path.extname(file).toLowerCase())||!fs.statSync(file).isFile())throw Error('not an allowed review file');
 }catch{res.writeHead(404);res.end('Read-only local review source unavailable');return;}
 const size=fs.statSync(file).size;let start=0,end=size-1;const range=req.headers.range;
 if(range){const m=/^bytes=(\d+)-(\d*)$/.exec(range);if(!m){res.writeHead(416);res.end();return;}start=Number(m[1]);if(m[2])end=Math.min(Number(m[2]),size-1);if(start>end){res.writeHead(416);res.end();return;}}
 const headers={'Content-Type':{'.html':'text/html;charset=utf-8','.mp4':'video/mp4','.png':'image/png'}[path.extname(file).toLowerCase()],'Accept-Ranges':'bytes','Content-Length':end-start+1,'Cache-Control':'no-store'};
 if(range)headers['Content-Range']=`bytes ${start}-${end}/${size}`;
 res.writeHead(range?206:200,headers);if(req.method==='HEAD')res.end();else fs.createReadStream(file,{start,end}).pipe(res);
});
server.listen(9270,'127.0.0.1',()=>console.log(JSON.stringify({startedAt:new Date().toISOString(),pid:process.pid,cwd:process.cwd(),port:9270,scope:'Read-only acquired/current review HTML/MP4/PNG only; no render or publishing'})));
