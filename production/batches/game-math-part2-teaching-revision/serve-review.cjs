// Local static review server; no CUDA, subprocesses, uploads or external access.
const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../../shared/output/game-math-part2-teaching-revision');
http.createServer((req,res)=>{
 const relative=decodeURIComponent(new URL(req.url,'http://localhost').pathname).replace(/^\//,'');
 let file=path.resolve(root,relative||'source-review/index.html');
 if(file!==root&&!file.startsWith(root+path.sep)){res.writeHead(403);return res.end();}
 try{if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');const size=fs.statSync(file).size;
 const type={'.html':'text/html; charset=utf-8','.mp4':'video/mp4','.png':'image/png','.jpg':'image/jpeg','.json':'application/json'}[path.extname(file)]||'application/octet-stream';
 const range=req.headers.range?.match(/^bytes=(\d+)-(\d*)$/);let start=0,end=size-1,status=200;
 if(range){start=Number(range[1]);end=range[2]?Math.min(Number(range[2]),end):end;status=206;if(start>end||start>=size){res.writeHead(416,{'Content-Range':`bytes */${size}`});return res.end();}}
 const headers={'Content-Type':type,'Content-Length':end-start+1,'Accept-Ranges':'bytes'};if(range)headers['Content-Range']=`bytes ${start}-${end}/${size}`;
 res.writeHead(status,headers);fs.createReadStream(file,{start,end}).pipe(res);
 }catch{res.writeHead(404);res.end('Missing review file');}
}).listen(9261,'127.0.0.1',()=>console.log('Local review: http://127.0.0.1:9261/source-review/index.html'));
