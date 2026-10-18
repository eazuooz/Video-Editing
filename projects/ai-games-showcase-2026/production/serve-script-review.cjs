// Local-only read-only review of this episode's script/PPT preview directory.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../output/ai-games-showcase-2026/planning');
const types={'.html':'text/html; charset=utf-8','.png':'image/png','.mp4':'video/mp4','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation'};
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
 let name;try{name=decodeURIComponent(new URL(req.url,'http://127.0.0.1:9235').pathname);}catch{res.writeHead(400).end();return;}
 const file=path.resolve(root,name==='/'?'index.html':name.replace(/^\/+/,'') );
 if(!file.startsWith(root+path.sep)||!types[path.extname(file)]){res.writeHead(403).end();return;}
 let stat;try{stat=fs.statSync(file);}catch{res.writeHead(404).end();return;}
 if(!stat.isFile()){res.writeHead(404).end();return;}
 let start=0,end=stat.size-1,status=200;const range=req.headers.range;
 if(range){const match=/^bytes=(\d+)-(\d*)$/.exec(range);if(!match){res.writeHead(416).end();return;}start=Number(match[1]);end=match[2]?Number(match[2]):end;if(start>end||end>=stat.size){res.writeHead(416).end();return;}status=206;res.setHeader('Content-Range',`bytes ${start}-${end}/${stat.size}`);}
 res.writeHead(status,{'Content-Type':types[path.extname(file)],'Content-Length':end-start+1,'Accept-Ranges':'bytes','Cache-Control':'no-cache'});
 if(req.method==='HEAD')res.end();else fs.createReadStream(file,{start,end}).pipe(res);
}).listen(9235,'127.0.0.1',()=>console.log('AI game script review: http://127.0.0.1:9235/'));
