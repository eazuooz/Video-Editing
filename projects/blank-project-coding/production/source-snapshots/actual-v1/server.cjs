const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),{spawn,spawnSync}=require('node:child_process');
const base=__dirname,work=path.join(base,'.runtime');fs.mkdirSync(work,{recursive:true});
const vc='C:\\Program Files\\Microsoft Visual Studio\\18\\Community\\VC\\Auxiliary\\Build\\vcvars64.bat';
const envBat=path.join(work,'build-env.cmd');fs.writeFileSync(envBat,`@echo off\r\ncall "${vc}" >nul\r\nset\r\n`);
const envResult=spawnSync('cmd.exe',['/d','/c',envBat],{encoding:'utf8',windowsHide:true});
if(envResult.status!==0)throw Error(envResult.stderr||'Cannot load MSVC');
const buildEnv={...process.env};for(const l of envResult.stdout.split(/\r?\n/)){const i=l.indexOf('=');if(i>0)buildEnv[l.slice(0,i)]=l.slice(i+1);}
let child=null,events=[],seq=0;const emit=e=>events.push({sequence:++seq,at:new Date().toISOString(),...e});
const json=(res,v,status=200)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(v));};
http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://127.0.0.1:9341');
  if(url.pathname==='/api/catalog')return json(res,require('./lessons.cjs'));
  if(url.pathname==='/api/events')return json(res,{events:events.filter(e=>e.sequence>Number(url.searchParams.get('after')||0))});
  if(url.pathname==='/api/step'){if(child)child.stdin.write('\n');return json(res,{ok:!!child});}
  if(url.pathname==='/api/stop'){if(child)child.kill();child=null;return json(res,{ok:true});}
  if(url.pathname==='/api/build'){
   let body='';for await(const chunk of req)body+=chunk;
   const {code}=JSON.parse(body);if(typeof code!=='string'||code.length>20000)throw Error('Invalid source');
   if(child){child.kill();child=null;}events=[];seq=0;
   const source=path.join(work,'lesson.cpp'),exe=path.join(work,'lesson.exe');fs.writeFileSync(source,code);
   const build=spawnSync('cl.exe',['/nologo','/EHsc','/std:c++17','/Od','/Zi',`/I${base}`,source,`/Fe:${exe}`,`/Fo:${path.join(work,'lesson.obj')}`,`/Fd:${path.join(work,'lesson.pdb')}`],{env:buildEnv,cwd:work,encoding:'utf8',windowsHide:true,timeout:30000});
   emit({type:'build',exitCode:build.status,text:(build.stdout||'')+(build.stderr||'')});
   if(build.status!==0)return json(res,{ok:false});
   child=spawn(exe,[],{cwd:work,windowsHide:true});let buffer='';
   child.stdout.on('data',d=>{buffer+=d.toString();let i;while((i=buffer.indexOf('\n'))>=0){const l=buffer.slice(0,i).trim();buffer=buffer.slice(i+1);try{emit(JSON.parse(l));}catch{if(l)emit({type:'stdout',text:l});}}});
   child.stderr.on('data',d=>emit({type:'stderr',text:d.toString()}));child.on('exit',exitCode=>{emit({type:'exit',exitCode});child=null;});return json(res,{ok:true});
  }
  const files={'/':'index.html','/app.js':'app.js','/engine.js':'engine.js','/style.css':'style.css'};
  const file=files[url.pathname];if(!file)return json(res,{error:'not found'},404);
  res.writeHead(200,{'Content-Type':file.endsWith('.html')?'text/html; charset=utf-8':file.endsWith('.css')?'text/css':'text/javascript'});res.end(fs.readFileSync(path.join(base,file)));
 }catch(e){json(res,{error:String(e)},500);}
}).listen(9341,'127.0.0.1',()=>console.log('Owned development workbench http://127.0.0.1:9341 — actual MSVC execution'));
