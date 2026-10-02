const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const input=JSON.parse(fs.readFileSync(path.join(root,'projects/game-writing/sources/source-files.json'),'utf8')).files;
const out=path.join(__dirname,'source-decode');fs.mkdirSync(out,{recursive:true});
(async()=>{const results=[];for(const source of input){
 const stem=path.basename(source.path,'.mp4'),log=fs.createWriteStream(path.join(out,stem+'.log'));
 const args=['-hide_banner','-v','error','-xerror','-threads','2','-i',source.path,'-f','null','-'];
 const child=spawn('ffmpeg',args,{cwd:root,windowsHide:true});let errors='';
 child.stderr.on('data',d=>{log.write(d);errors+=d});child.stdout.pipe(log,{end:false});
 fs.writeFileSync(path.join(out,'runner.json'),JSON.stringify({pid:process.pid,childPid:child.pid,startedAt:new Date().toISOString(),source:source.path,args,status:'decoding'},null,2));
 const code=await new Promise((resolve,reject)=>{child.on('error',reject);child.on('exit',resolve)});log.end();
 results.push({source:source.path,sourceSha256:source.sha256,exitCode:code,errorOutput:errors,fullDecodePassed:code===0&&errors.trim()==='',log:`projects/game-writing/production/source-decode/${stem}.log`});
 console.log(`${stem}: full decode ${code===0&&errors.trim()===''?'passed':'needs review'}`);
 }
 const passed=results.every(r=>r.fullDecodePassed);fs.writeFileSync(path.join(__dirname,'source-decode.json'),JSON.stringify({finishedAt:new Date().toISOString(),passed,results},null,2)+'\n');
 fs.writeFileSync(path.join(out,'runner.json'),JSON.stringify({pid:process.pid,status:'finished',passed,finishedAt:new Date().toISOString()},null,2));
 if(!passed)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
