const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history/local/caption-frame-boundary-v6',renders='production/research/game-lighting-history/local/episode03-chapter-render-v4/renders';
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,p))).digest('hex');
const planPath=base+'/plan.json',plan=read(planPath),video=renders+'/caption-frame-boundary-project-v6.mp4',execution=renders+'/caption-frame-boundary-project-v6.execution.json',e=read(execution),dest=base+'/extraction.json',dir=base+'/qa';
if(fs.existsSync(path.join(root,dest))||fs.existsSync(path.join(root,dir)))throw Error('Existing extraction preserved');
const metadataSerialization=[];
for(const i of plan.inputs)if(sha(i.path)!==i.sha256){
 const s=fs.readFileSync(path.join(root,i.path),'utf8'),normalized=crypto.createHash('sha256').update(s.replace(/\r\n/g,'\n').trimEnd()+'\n').digest('hex');
 if(!i.path.endsWith('.meta')||normalized!==i.sha256)throw Error('Changed input:'+i.path);
 metadataSerialization.push({path:i.path,preparedSha256:i.sha256,actualSha256:sha(i.path),normalizedSha256:normalized,reason:'Editor removed terminal newline only; every metadata value and all render inputs unchanged. Initial pre-extraction guard rejection preserved in this verification.'});
}
if(e.status!=='complete'||e.exitCode!==0||!e.command.includes('caption-frame-boundary-project-v6.mp4'))throw Error('Exporter completion required');
const resources=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' -or $_.Name -match '^python(w)?\\.exe$' -and $_.CommandLine -match 'review-.*game-lighting|review-episode04' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(resources.status!==0||resources.stdout.trim())throw Error('Single owned media slot busy');
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const startedAt=new Date().toISOString(),statePath=base+'/qa-execution.json';
function state(x){fs.writeFileSync(path.join(root,statePath),JSON.stringify({startedAt,pid:process.pid,command:process.argv,cwd:root,cpuThreads:2,gpuJobs:0,...x},null,2)+'\n');}
function run(exe,args,step,binary=false){state({status:'running',step,childCommand:[exe,...args]});const r=spawnSync(exe,args,{encoding:binary?undefined:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(step+':'+r.stderr);return r.stdout;}
try{
 const probe=JSON.parse(run(ffprobe,['-v','error','-count_frames','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_read_frames,duration','-of','json',path.join(root,video)],'probe'));
 const v=probe.streams[0];if(probe.streams.length!==1||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||v.time_base!=='1/90000'||Number(v.nb_read_frames)!==plan.plannedFrames)throw Error('Video format/frame mismatch');
 const pts=JSON.parse(run(ffprobe,['-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','json',path.join(root,video)],'pts')).packets.map(x=>x.pts).sort((a,b)=>a-b);
 if(pts.length!==plan.plannedFrames||pts.some((x,i)=>x!==i*1500))throw Error('Discontinuous PTS');
 run(ffmpeg,['-v','error','-threads','2','-i',path.join(root,video),'-f','null','NUL'],'whole-decode');
 fs.mkdirSync(path.join(root,dir),{recursive:true});
 const frames=plan.samples.map(x=>({...x,frame:x.outputSampleFrame})),selection=frames.map(x=>`eq(n,${x.frame})`).join('+');
 run(ffmpeg,['-v','error','-nostdin','-threads','2','-i',path.join(root,video),'-vf',`select='${selection}'`,'-vsync','0','-threads','2',path.join(root,dir,'frame-%03d.png')],'extract');
 const cropped=run(ffmpeg,['-v','error','-nostdin','-threads','2','-i',path.join(root,video),'-vf',`select='${selection}',crop=20:20:220:946,format=gray`,'-vsync','0','-threads','2','-f','rawvideo','pipe:1'],'caption-box-presence',true);
 if(cropped.length!==frames.length*400)throw Error('Crop sample count mismatch');
 frames.forEach((x,i)=>{x.path=dir+'/frame-'+String(i+1).padStart(3,'0')+'.png';x.sha256=sha(x.path);const p=cropped.subarray(i*400,(i+1)*400);x.captionBoxMean=p.reduce((a,b)=>a+b,0)/400;x.expectedCaptionVisible=Boolean(x.expectedText);x.boxPresenceMatches=x.expectedCaptionVisible?x.captionBoxMean>220:x.captionBoxMean<10;});
 const boards=[];for(let i=0;i<Math.ceil(frames.length/6);i++){const f=dir+'/board-'+String(i+1).padStart(2,'0')+'.png',n=Math.min(6,frames.length-i*6);run(ffmpeg,['-v','error','-nostdin','-threads','2','-start_number',String(i*6+1),'-i',path.join(root,dir,'frame-%03d.png'),'-vf',`scale=960:540,tile=2x3:nb_frames=${n}`,'-frames:v','1','-threads','2',path.join(root,f)],'board-'+(i+1));boards.push({path:f,sha256:sha(f),samples:frames.slice(i*6,i*6+n),directlyRead:false});}
 const record={verifiedAt:new Date().toISOString(),scope:'Caption boundary implementation only; actual encoded fourteen held frame cases. No full episode/native/final runtime adoption.',plan:{path:planPath,sha256:sha(planPath)},video:{path:video,sha256:sha(video)},exporter:{path:execution,...e},metadataSerialization,probe,exactContinuousPts:true,wholeDecodeExitCode:0,frames,boards,allCaptionBoxPresenceMatches:frames.every(x=>x.boxPresenceMatches),directPixelsReviewed:false,finalRuntimeAdopted:false,allFinalPixelsReviewed:false,localOnly:true};
 fs.writeFileSync(path.join(root,dest),JSON.stringify(record,null,2)+'\n');state({status:'complete-awaiting-direct-pixel-review',exitCode:0,endedAt:new Date().toISOString(),frames:frames.length,boards:boards.length});console.log(JSON.stringify({videoFrames:pts.length,samples:frames.length,boards:boards.length,boxMatches:record.allCaptionBoxPresenceMatches}));
}catch(error){state({status:'failed-preserving-produced-files',error:String(error),endedAt:new Date().toISOString()});throw error;}
