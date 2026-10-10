const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history',out=path.join(root,b,'local/episode03-native-crop-v10'),ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(x)).digest('hex');
const resources=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CreationDate | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(resources.status!==0||resources.stdout.trim())throw Error('Owned media slot busy');
const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],{encoding:'utf8',windowsHide:true});if(gpu.status!==0)throw Error('GPU observation failed');
const sources=new Map();for(const v of [3,5,6,7,8])for(const a of read(`${b}/local/episode03-native-v${v}/execution.json`).completed)sources.set(a.slug,a);
const definitions=[
 ['lumen-content-examples-2021',[42,61,106,190,241,256,270,361,394,405,480,498,536,600,672,685,705,737],'crop=1280:720:0:20','crop=1280:720:640:20'],
 ['nanite-editor-motion-2021',[118,200,232,322,466,490,610,657,705,742,814],'crop=1440:810:480:0'],
 ['rtxgi-ue5-preview2-2022',[214,268,296,386],null],
 ['hardware-rt-ue5-preview2-2022',[179,207],null],
 ['dlss-ue5-preview2-2022',[196,225,263],null],
 ['nvrtx-showcase-2021',[18,43,64,75],null],
 ['escape-naraka-rtxgi-2021',[20],null],
 ['control-dlss2-2020',[8],null],
 ['battlefield-v-rtx-2018',[24],null],
 ['deliver-moon-dlss2-2020',[11],null],
 ['wolfenstein-dlss2-2020',[44],null],
 ['rtxdi-boulevard-2021',[45],null]
];
const points=[];for(const [slug,times,crop,cropB] of definitions){const a=sources.get(slug);if(!a)throw Error('Missing actual source '+slug);if(sha(path.join(root,a.media))!==a.sha256)throw Error('Source changed '+slug);for(const seconds of times)points.push({slug,seconds,crop,cropB,media:a.media,sourceSha256:a.sha256,purpose:'Native-resolution UI labels, presenter exclusion and retained relevant viewport; sampled frame only, no continuous-motion or final-caption approval'});}
fs.mkdirSync(out,{recursive:true});const sp=path.join(out,'execution.json');if(fs.existsSync(sp))throw Error('Preserve existing crop execution');let current=null,completed=[];
const state=x=>fs.writeFileSync(sp,JSON.stringify({startedAt,parentPid:process.pid,command:process.argv,cwd:root,threads:2,gpuJobs:0,gpuObserved:gpu.stdout.trim(),current,points:points.length,completed,localOnly:true,allFinalPixelsReviewed:false,...x},null,2)+'\n'),startedAt=new Date().toISOString();
const run=(label,args)=>new Promise((resolve,reject)=>{const h=fs.openSync(path.join(out,label+'.log'),'a'),p=spawn(ff,args,{cwd:root,windowsHide:true,stdio:['ignore',h,h]});current={label,pid:p.pid,command:[ff,...args],startedAt:new Date().toISOString()};state({status:'running'});p.on('error',reject);p.on('close',code=>{fs.closeSync(h);current.exitCode=code;current.endedAt=new Date().toISOString();state({status:code===0?'step-complete':'failed'});code===0?resolve():reject(Error(label+' exit'+code));});});
(async()=>{for(let i=0;i<points.length;i++){const p=points[i],id=String(i+1).padStart(3,'0')+'-'+p.slug+'-'+p.seconds,original=path.join(out,id+'.raw.png');await run(id+'-raw',['-v','error','-threads','2','-ss',String(p.seconds),'-i',path.join(root,p.media),'-frames:v','1','-threads','2',original]);const images=[{role:'raw',path:path.relative(root,original).replaceAll('\\','/'),sha256:sha(original)}];
 for(const [role,filter] of [['viewport',p.crop],['controls',p.cropB]])if(filter){const file=path.join(out,id+'.'+role+'.png');await run(id+'-'+role,['-v','error','-threads','2','-i',original,'-vf',filter+',scale=1920:1080','-frames:v','1','-threads','2',file]);images.push({role,path:path.relative(root,file).replaceAll('\\','/'),sha256:sha(file),filter});}
 const board=path.join(out,id+'.board.png'),inputs=images.map(x=>['-i',path.join(root,x.path)]).flat(),fc=images.map((x,n)=>`[${n}:v]scale=640:360,pad=640:390:0:30:color=0x101418,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='${p.slug} ${p.seconds}s ${x.role}':x=6:y=5:fontsize=16:fontcolor=white[v${n}]`).join(';')+';'+images.map((_,n)=>`[v${n}]`).join('')+`hstack=inputs=${images.length}[board]`;
 if(images.length===1)await run(id+'-board',['-v','error','-threads','2','-i',original,'-vf',"scale=1280:720,pad=1280:750:0:30:color=0x101418,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='"+p.slug+' '+p.seconds+"s raw':x=6:y=5:fontsize=20:fontcolor=white",'-frames:v','1','-threads','2',board]);else await run(id+'-board',['-v','error','-threads','2',...inputs,'-filter_complex_threads','2','-filter_complex',fc,'-map','[board]','-frames:v','1','-threads','2',board]);
 completed.push({...p,images,board:{path:path.relative(root,board).replaceAll('\\','/'),sha256:sha(board),directlyViewed:false},fullMotionReviewed:false,finalUseApproved:false});current=null;state({status:'point-complete'});console.log(JSON.stringify({completed:completed.length,total:points.length,slug:p.slug,seconds:p.seconds}));}
state({status:'native-crop-samples-ready',completedAt:new Date().toISOString()});})().catch(e=>{state({status:'failed',error:e.stack});console.error(e);process.exitCode=1;});
