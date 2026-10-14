// One silent, CPU2 source acquisition after the corrected-context worker closes.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawn,spawnSync}=require('child_process');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history/local/episode04-tsr-browser-v3',out=path.join(root,base);
const py=path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),bin='C:/ProgramData/HP/LCDDisplayHelper/bin',probe=bin+'/ffprobe.exe',ffmpeg=bin+'/ffmpeg.exe';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const old=read('projects/game-lighting-history-04/production/additive-context-session-v2.json');
if(!old.sessionClosed||old.exitCode!==0||old.actualIdentityLive||!old.correctedContextsApproved)throw Error('Actual closed reviewed corrected contexts required');
const candidatePath='projects/game-lighting-history-04/production/tsr-browser-candidate-review-v3.json';
const candidate=read(candidatePath);
const guard=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { ($_.Name -eq 'ffmpeg.exe' -or $_.Name -eq 'python.exe' -or $_.Name -eq 'node.exe') -and $_.CommandLine -match 'game-lighting-history' -and $_.CommandLine -notmatch 'vite|acquire-episode04-tsr-browser-v3' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(guard.status!==0||guard.stdout.trim())throw Error('Another owned heavy job is live');
const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],{encoding:'utf8',windowsHide:true});if(gpu.status!==0)throw Error('Resource observation failed');
if(fs.existsSync(out))throw Error('Existing acquisition directory preserved; diagnose rather than repeat');
fs.mkdirSync(out,{recursive:true});
const state={startedAt:new Date().toISOString(),status:'prepared',coordinatorPid:process.pid,command:[process.execPath,...process.argv.slice(1)],cwd:root,cpuThreads:2,gpuJobs:0,gpuObservation:gpu.stdout.trim(),candidate:{path:candidatePath,sha256:sha(path.join(root,candidatePath))},current:null,completed:[],rightsApproved:false,recentUseCheckPassed:false,finalUseApproved:false,localOnly:true};
const statePath=path.join(out,'execution.json');
function write(){const tmp=statePath+'.writing';fs.writeFileSync(tmp,JSON.stringify(state,null,2)+'\n');fs.renameSync(tmp,statePath);}
function run(label,cmd,args){return new Promise((resolve,reject)=>{
 const log=fs.createWriteStream(path.join(out,label+'.log'));
 const child=spawn(cmd,args,{cwd:root,env:{...process.env,OMP_NUM_THREADS:'2',MKL_NUM_THREADS:'2',CUDA_VISIBLE_DEVICES:'-1'},windowsHide:true});
 state.status=label;state.current={label,pid:child.pid,command:[cmd,...args],startedAt:new Date().toISOString(),log:path.relative(root,path.join(out,label+'.log')).replaceAll('\\','/')};write();
 child.stdout.pipe(log);child.stderr.pipe(log);
 child.on('error',reject);child.on('close',code=>{log.end();state.lastExit={...state.current,exitCode:code,endedAt:new Date().toISOString()};state.current=null;write();code===0?resolve():reject(Error(label+' exit '+code));});
});}
(async()=>{
 for(const [name,window] of [['mannequin-low-resolution',[720,760]],['fan-motion-vectors',[858,892]]]){
  const file=path.join(out,name+'.mp4'),meta=path.join(out,name+'.info.json');
  await run(name+'-download',py,['-X','utf8','-m','yt_dlp','--no-progress','--http-chunk-size','1M','--ffmpeg-location',bin,'--download-sections','*'+window.join('-'),'--force-keyframes-at-cuts','--downloader-args','ffmpeg_i:-threads 2','--downloader-args','ffmpeg_o:-threads 2','--no-playlist','--no-overwrites','--write-info-json','--no-write-thumbnail','--js-runtimes','node:'+process.execPath,'--retries','2','--fragment-retries','2','--socket-timeout','30','-f','bv*[height<=1080][ext=mp4][vcodec^=avc]/bv*[height<=1080][ext=mp4]','-o',path.join(out,name+'.%(ext)s'),'https://www.youtube.com/watch?v=szgnZx2b0Zg']);
  const info=JSON.parse(fs.readFileSync(meta,'utf8'));
  const p=spawnSync(probe,['-v','error','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,time_base,nb_frames:format=duration,size','-of','json',file],{encoding:'utf8',windowsHide:true});if(p.status!==0)throw Error('Actual probe failed');const actual=JSON.parse(p.stdout);
  if(actual.streams.some(s=>s.codec_type==='audio'))throw Error('Only silent source acquisition allowed');
  await run(name+'-whole-window-decode',ffmpeg,['-v','error','-threads','2','-i',file,'-f','null','-']);
  state.completed.push({id:'szgnZx2b0Zg',name,requestedSourceWindow:window,forceKeyframesAtCuts:true,sourceStartOffsetVerified:false,media:path.relative(root,file).replaceAll('\\','/'),sha256:sha(file),info:path.relative(root,meta).replaceAll('\\','/'),infoSha256:sha(meta),title:info.title,publisher:info.channel,channelId:info.channel_id,uploadDate:info.upload_date,probe:actual,wholeWindowDecodeExit:0,wholeOriginalDecoded:false,sourceAudioAcquired:false,normalMotionReviewed:false,cropAndTrackedAnnotationReviewed:false,rightsApproved:false,recentUseCheckPassed:false,finalUseApproved:false});write();
 }
 state.status='two-native-windows-acquired-awaiting-direct-motion-and-offset-review';state.exitCode=0;state.endedAt=new Date().toISOString();write();console.log(JSON.stringify({completed:state.completed.length,sourceSeconds:74,finalUseApproved:false}));
})().catch(e=>{state.status='failed-preserving-source-and-logs';state.error=e.stack;state.exitCode=1;state.endedAt=new Date().toISOString();write();console.error(e);process.exitCode=1;});
