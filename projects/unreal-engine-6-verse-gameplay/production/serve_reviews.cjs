// Serve the two locally approved review scopes without exposing the worktree.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../..');
const newsReview = process.argv.includes('--newsroom');
const selected = process.argv.includes('--a01kit') ? {
  kit: ['animation-assigning', 'unreal-kit-v2'],
} : process.argv.includes('--a03') ? {
  a03: ['animation-breaking-down-attack-animations', 'grid-v1'],
} : newsReview ? {
  news: ['unreal-engine-6-verse-gameplay', 'newsroom-v3'],
  a01: ['animation-assigning', 'grid-v1'],
} : {
  ue6: ['unreal-engine-6-verse-gameplay', 'engine-comparison-v2'],
  a02: ['animation-exaggeration', 'fighters-v4-kula-lili'],
};
const allowed = new Map();
for (const [key, [slug, revision]] of Object.entries(selected)) {
  const dir = path.join(root,'projects',slug,'production','local',revision,'delivery','output',slug);
  for (const name of ['index.html', ...['captioned.mp4','clean.mp4','ko.srt','en.srt'].map(ext => slug+'.'+ext),'sources.txt','delivery-manifest.json']) {
    const file=path.join(dir,name);
    allowed.set('/'+key+'/'+name, file);
  }
}
const types={'.mp4':'video/mp4','.html':'text/html; charset=utf-8','.srt':'application/x-subrip; charset=utf-8','.txt':'text/plain; charset=utf-8','.json':'application/json'};
const port=Number(process.argv[2]||9243);
const server=http.createServer((req,res)=>{
  if (!['GET','HEAD'].includes(req.method)) return res.writeHead(405).end();
  if (![String('localhost:'+port),String('127.0.0.1:'+port)].includes(req.headers.host))return res.writeHead(403).end();
  let key;try{key=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);}catch{return res.writeHead(400).end();}
  if (key==='/' || key==='/index.html') {
    const titles={ue6:'언리얼·고도·유니티 비교',a02:'동작의 과장 · 쿨라와 리리',news:'언리얼 6 발표 · 에픽 공식 시연과 도쿄 보도',a01:'애니메이션 제작 지시',kit:'애니메이션 제작 지시 · 언리얼 시연',a03:'공격 동작의 단계'};
    const entries=Object.keys(selected).filter(id=>fs.existsSync(allowed.get('/'+id+'/index.html')))
      .map(id=>'<li><a href="/'+id+'/">'+titles[id]+'</a></li>').join('');
    const body='<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>검수 영상</title><style>body{max-width:48rem;margin:4rem auto;padding:0 1.4rem;font:18px/1.8 sans-serif}a{color:#086452}</style><h1>검수 영상</h1><ul>'+entries+'</ul></html>';
    res.writeHead(200,{'Content-Type':'text/html; charset=utf-8','Content-Length':Buffer.byteLength(body)});
    return res.end(req.method==='HEAD'?undefined:body);
  }
  if (Object.hasOwn(selected,key.replace(/^\//,'').replace(/\/$/,'')))return res.writeHead(302,{Location:key.replace(/\/?$/,'/')+'index.html'}).end();
  const file=allowed.get(key);if(!file||!fs.existsSync(file))return res.writeHead(404).end();
  const size=fs.statSync(file).size;
  let a=0,b=size-1,status=200;
  const headers={'Content-Type':types[path.extname(file)],'Accept-Ranges':'bytes','Cache-Control':'no-cache','X-Content-Type-Options':'nosniff'};
  if(req.headers.range){
    const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
    if(!m||(!m[1]&&!m[2]))return res.writeHead(416).end();
    a=m[1]?Number(m[1]):Math.max(0,size-Number(m[2]));
    b=m[1]&&m[2]?Math.min(size-1,Number(m[2])):size-1;
    if(!Number.isSafeInteger(a)||!Number.isSafeInteger(b)||a>b||a>=size)return res.writeHead(416,{'Content-Range':'bytes */'+size}).end();
    status=206;headers['Content-Range']='bytes '+a+'-'+b+'/'+size;
  }
  headers['Content-Length']=b-a+1;res.writeHead(status,headers);
  if(req.method==='HEAD')return res.end();
  fs.createReadStream(file,{start:a,end:b}).on('error',()=>res.destroy()).pipe(res);
});
server.listen(port,'127.0.0.1');
