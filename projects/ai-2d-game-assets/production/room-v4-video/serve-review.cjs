const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve('C:/Users/1/Videos/YamyamCoding/ai-2d-room-v4-video/video/review'),port=9287;
const mime={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.srt':'text/plain; charset=utf-8','.md':'text/plain; charset=utf-8','.zip':'application/zip','.jpg':'image/jpeg','.png':'image/png'};
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
 if(!['127.0.0.1:'+port,'localhost:'+port].includes(req.headers.host)){res.writeHead(403).end();return;}
 let pathname;try{pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400).end();return;}
 const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
 if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
 fs.stat(file,(err,stat)=>{
  if(err||!stat.isFile()){res.writeHead(404).end();return;}
  const headers={'Content-Type':mime[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};let start=0,end=stat.size-1,status=200;
  if(req.headers.range){const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!m){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`}).end();return;}start=+m[1];end=m[2]?Math.min(+m[2],end):end;if(start>end){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`}).end();return;}status=206;headers['Content-Range']=`bytes ${start}-${end}/${stat.size}`;}
  headers['Content-Length']=end-start+1;res.writeHead(status,headers);if(req.method==='HEAD'){res.end();return;}const stream=fs.createReadStream(file,{start,end});stream.on('error',()=>res.destroy());stream.pipe(res);res.on('close',()=>stream.destroy());
 });
}).listen(port,'127.0.0.1',()=>process.stdout.write(`Review: http://127.0.0.1:${port}/\n`));
