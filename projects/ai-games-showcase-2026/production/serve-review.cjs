// Read-only loopback media review; only this episode's explicit media roots.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const repo=path.resolve(__dirname,'../../..');
const roots={source:path.join(repo,'production/preflight/ai-games-showcase-2026/local'),edit:path.join(__dirname,'local/compact-edit'),output:path.join(repo,'output/ai-games-showcase-2026')};
const types={'.mp4':'video/mp4','.wav':'audio/wav','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.html':'text/html; charset=utf-8'};
const movies=['fish-creator-demo.mp4','nightshoal-trailer.mp4','nightshoal-week11.mp4','vector-creator-demo.mp4','rally-creator-demo.mp4'];
function page(){
 let scenes=[];try{scenes=JSON.parse(fs.readFileSync(path.join(__dirname,'edit-plan.json'),'utf8')).scenes;}catch{}
 return '<!doctype html><meta charset="utf-8"><title>AI 게임 영상 검수</title><style>body{background:#090909;color:white;font:18px sans-serif;margin:20px}video{width:90vw;max-height:78vh}button,input{font-size:18px;margin:6px}</style><video id="v" controls muted preload="metadata" src="/source/fish-creator-demo.mp4"></video><div>'+movies.map(m=>`<button onclick="v.src='/source/${m}';v.play()">${m}</button>`).join('')+'<button onclick="v.src=\'/edit/ai-games-captioned.mp4\';v.play()">완성 검수본</button><button onclick="v.src=\'/edit/layout-sample.mp4\';v.play()">배치 샘플</button></div><button onclick="v.currentTime=Math.max(0,v.currentTime-5)">5초 이전</button><button onclick="v.currentTime+=5">5초 다음</button><label>이동할 초 <input id="seek" type="number" min="0" value="0"></label><button onclick="v.currentTime=Number(seek.value);v.play()">이동 재생</button><div>'+scenes.map(s=>`<button onclick="v.currentTime=${s.startFrame/60};v.play()">${s.id} ${s.title}</button>`).join('')+'</div>';
}
http.createServer((req,res)=>{
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405).end();return;}
 const u=new URL(req.url,'http://127.0.0.1:9236');if(u.pathname==='/'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'}).end(page());return;}
 let parts;try{parts=decodeURIComponent(u.pathname).split('/').filter(Boolean);}catch{res.writeHead(400).end();return;}
 const root=roots[parts.shift()];if(!root){res.writeHead(404).end();return;}const file=path.resolve(root,...parts),type=types[path.extname(file)];
 if(!type||!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}let stat;try{stat=fs.statSync(file);}catch{res.writeHead(404).end();return;}
 let start=0,end=stat.size-1,status=200;const range=req.headers.range;
 if(range){let m=/^bytes=(\d+)-(\d*)$/.exec(range);if(!m){res.writeHead(416).end();return;}start=+m[1];end=m[2]?+m[2]:end;if(start>end||end>=stat.size){res.writeHead(416).end();return;}status=206;res.setHeader('Content-Range',`bytes ${start}-${end}/${stat.size}`);}
 res.writeHead(status,{'Content-Type':type,'Content-Length':end-start+1,'Accept-Ranges':'bytes','Cache-Control':'no-cache'});if(req.method==='HEAD')res.end();else fs.createReadStream(file,{start,end}).pipe(res);
}).listen(9236,'127.0.0.1',()=>console.log('Selected video review on127.0.0.1:9236'));
