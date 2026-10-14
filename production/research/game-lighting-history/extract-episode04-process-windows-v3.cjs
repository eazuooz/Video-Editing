const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const base='production/research/game-lighting-history/local/episode04-process-v3';
const out=path.join(root,base),ffmpeg='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';
const sources={
 hair:{file:'production/research/game-lighting-history/local/episode04-native-v2/strand-hair-editor-ue426-2021.mp4',sha256:'63cd36424f88e7e687ef104ee242289f02dbf58f93cd455d52879db2efb22a75'},
 post:{file:'production/research/game-lighting-history/local/epic-post-processing.mp4',sha256:'d4c422af11f1242fb9d1ac8fd233ddd5638dbfc4be6a93417e50d826f92ea723'},
};
const windows=[
 {id:'hair-debug',source:'hair',start:558,end:635,spacing:4},
 {id:'hair-material',source:'hair',start:650,end:835,spacing:6},
 {id:'hair-physics',source:'hair',start:1000,end:1135,spacing:6},
 {id:'hair-lod',source:'hair',start:1390,end:1755,spacing:8},
 {id:'post-exposure',source:'post',start:1380,end:1720,spacing:10},
 {id:'post-bloom-film',source:'post',start:1735,end:1975,spacing:8},
 {id:'post-dof-before',source:'post',start:2050,end:2255,spacing:8},
 {id:'post-dof-after',source:'post',start:2305,end:2540,spacing:8},
];
const check=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'ffmpeg|python|node' -and $_.CommandLine -match 'game-lighting-history' -and $_.CommandLine -notmatch 'vite|extract-episode04-process-windows-v3|Get-CimInstance' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(check.status!==0||check.stdout.trim())throw Error('Owned single media slot busy: inspect identity');
const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],{encoding:'utf8',windowsHide:true});
if(gpu.status!==0)throw Error('Resource observation failed');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
for(const s of Object.values(sources))if(hash(path.join(root,s.file))!==s.sha256)throw Error('Preserved source changed');
if(fs.existsSync(out))throw Error('Preserve existing extraction; do not repeat');
fs.mkdirSync(out,{recursive:true});
let current=null;const completed=[],startedAt=new Date().toISOString();
const write=extra=>fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify({schemaVersion:1,startedAt,parentPid:process.pid,command:process.argv,cwd:root,cpuThreads:2,gpuJobs:0,gpuObserved:gpu.stdout.trim(),sources,windows,completed,current,allBoardsDirectlyRead:false,allMotionApproved:false,finalUseApproved:false,localOnly:true,...extra},null,2)+'\n');
async function run(w){
 const dir=path.join(out,w.id);fs.mkdirSync(dir);const s=sources[w.source];
 // Bound input frames before tile batching: output -t alone can let the last
 // contact sheet contain samples beyond the requested source end. Preserve the
 // existing 43 exploratory boards; this change applies only to a future run.
 const filter=`trim=duration=${w.end-w.start},setpts=PTS-STARTPTS,fps=1/${w.spacing},scale=800:450,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='${w.id} +%{pts\\:hms} from ${w.start}s':x=6:y=6:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.8,tile=3x2:nb_frames=6:padding=4:margin=4`;
 const args=['-v','error','-threads','2','-ss',String(w.start),'-i',path.join(root,s.file),'-t',String(w.end-w.start),'-vf',filter,'-vsync','0','-threads','2',path.join(dir,'board-%03d.png')];
 await new Promise((resolve,reject)=>{const log=fs.openSync(path.join(dir,'extract.log'),'a'),p=spawn(ffmpeg,args,{cwd:root,windowsHide:true,env:{...process.env,OMP_NUM_THREADS:'2'},stdio:['ignore',log,log]});current={id:w.id,pid:p.pid,executable:ffmpeg,args,startedAt:new Date().toISOString()};write({status:'running'});p.on('error',e=>{fs.closeSync(log);reject(e)});p.on('close',code=>{fs.closeSync(log);if(code!==0)return reject(Error(w.id+' exit '+code));resolve();});});
 const boards=fs.readdirSync(dir).filter(n=>/^board-\d+\.png$/.test(n)).sort().map(n=>({path:path.relative(root,path.join(dir,n)).replaceAll('\\','/'),sha256:hash(path.join(dir,n)),directlyRead:false}));
 completed.push({...w,sourceSha256:s.sha256,actualExit:0,boards,frameTimestampScope:'Relative filter timestamps start near zero; add the recorded start. Boundary/motion approval requires exact native playback, not these sampling labels.'});current=null;write({status:'window-complete'});console.log(JSON.stringify({window:w.id,boards:boards.length,finalUseApproved:false}));
}
(async()=>{write({status:'started'});for(const w of windows)await run(w);write({status:'all-window-samples-ready',completedAt:new Date().toISOString(),next:'Read every board, then verify exact selected intervals at original playback speed and their crop/annotations/caption clearance. Preserve raw history and no final approval from sampled frames.'});})().catch(e=>{write({status:'failed',error:e.stack});console.error(e);process.exitCode=1;});
