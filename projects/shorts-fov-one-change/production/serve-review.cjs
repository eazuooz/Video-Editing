// Read-only local review of this exact final Short; no listings or writes.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const file=path.join(__dirname,'local/shorts-fov-one-change.captioned.mp4');
const page='<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>얌얌코딩 FOV 쇼츠 검수</title><style>body{background:#202020;color:white;font:16px sans-serif;margin:10px}video{width:375px;max-width:94vw}button{font-size:16px;margin:6px}</style><video id="v" src="/video.mp4" controls muted preload="metadata"></video><div><button onclick="v.currentTime=0;v.play()">처음부터 재생</button><button onclick="v.currentTime=8;v.play()">중앙 대상 비교</button><button onclick="v.currentTime=13;v.play()">좁히는 전환</button><button onclick="v.currentTime=24;v.play()">마지막 정리</button><button onclick="v.pause()">일시정지</button></div>';
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
 if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store'}).end(page);return;}
 if(req.url!=='/video.mp4'||!fs.existsSync(file)){res.writeHead(404).end();return;}
 const stat=fs.statSync(file);let a=0,b=stat.size-1,code=200;
 if(req.headers.range){const m=/^bytes=(\d+)-(\d*)$/.exec(req.headers.range);if(!m){res.writeHead(416).end();return;}a=+m[1];b=m[2]?+m[2]:b;if(a>b||b>=stat.size){res.writeHead(416).end();return;}code=206;res.setHeader('Content-Range',`bytes ${a}-${b}/${stat.size}`);}
 res.writeHead(code,{'Content-Type':'video/mp4','Content-Length':b-a+1,'Accept-Ranges':'bytes','Cache-Control':'no-store'});if(req.method==='HEAD')res.end();else fs.createReadStream(file,{start:a,end:b}).pipe(res);
}).listen(9243,'127.0.0.1',()=>console.log('FOV Short review http://127.0.0.1:9243/'));
