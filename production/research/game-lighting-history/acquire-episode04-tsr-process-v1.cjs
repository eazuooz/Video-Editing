const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history/local/episode04-tsr-process-v1',out=path.join(root,base);
const bin='C:/ProgramData/HP/LCDDisplayHelper/bin',ffmpeg=bin+'/ffmpeg.exe',ffprobe=bin+'/ffprobe.exe';
const primary='https://dev.epicgames.com/documentation/unreal-engine/temporal-super-resolution-in-unreal-engine';
const requests=[
 {id:'tsr-disocclusion',url:'https://d1iv7db44yhgxn.cloudfront.net/documentation/images/ba43f68c-cbf5-474d-a756-dd98846718d1/tsr-parallax-disocclusion.gif',focus:'Moving camera reveals a distant building behind a nearer one; document labels Epic scalability and50percent internal screen percentage.'},
 {id:'tsr-flicker-off',url:'https://d1iv7db44yhgxn.cloudfront.net/documentation/images/bfc8c77b-7b14-4cc5-913b-381d33c4b582/tsr-flickering-1.gif',focus:'Document worst-case grazing-angle geometric shimmer with flickering shading rejection disabled; exact pairing and scene framing require direct review.'},
 {id:'tsr-flicker-on',url:'https://d1iv7db44yhgxn.cloudfront.net/documentation/images/3039d92e-612c-4d52-be57-e52579a93975/tsr-flickering-2.gif',focus:'Document corresponding rejection-enabled/increased-period example; settings differ and this is not a universal performance benchmark.'},
 {id:'tsr-camera-recede',url:'https://d1iv7db44yhgxn.cloudfront.net/documentation/images/c575ee21-a5fa-4099-8d0f-a812bea49a91/tsr-antiflickering-1.gif',focus:'Camera pulls back; document describes changed moire location and delayed classification over several frames.'}
];
const resuming=process.argv.includes('--resume-even-padding-v2');
const originalState=path.join(out,'execution.json'),statePath=path.join(out,resuming?'execution-v2.json':'execution.json');
if(fs.existsSync(out)&&!resuming)throw Error('Preserve prior acquisition; inspect its real state instead');
if(resuming&&(!fs.existsSync(originalState)||JSON.parse(fs.readFileSync(originalState,'utf8')).status!=='failed'||fs.existsSync(statePath)))throw Error('Only the diagnosed failed v1 can resume once');
const guard=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('python.exe','ffmpeg.exe','node.exe') -and $_.CommandLine -match 'game-lighting-history' -and $_.CommandLine -notmatch 'vite|acquire-episode04-tsr-process-v1|powershell' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});
if(guard.status!==0||guard.stdout.trim())throw Error('Owned processing slot busy');
const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],{encoding:'utf8',windowsHide:true});if(gpu.status!==0)throw Error('Resource observation failed');
fs.mkdirSync(out,{recursive:true});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const state={schemaVersion:1,startedAt:new Date().toISOString(),parentPid:process.pid,command:process.argv,cwd:root,cpuThreads:2,gpuJobs:0,gpuObserved:gpu.stdout.trim(),primary,requests,completed:[],current:null,sourceAudioUsed:false,loopedForQuota:false,finalUseApproved:false,priorFailure:resuming?{path:path.relative(root,originalState).replaceAll('\\','/'),sha256:sha(originalState),cause:'743pixel source width cannot encode yuv420p; pad at most one black pixel on right/bottom, retain original GIF and failed output.'}:null};
const write=()=>fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');
const run=(label,exe,args)=>new Promise((resolve,reject)=>{const fd=fs.openSync(path.join(out,label+'.log'),'a'),child=spawn(exe,args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});state.current={label,pid:child.pid,exe,args,startedAt:new Date().toISOString()};write();child.on('error',reject);child.on('close',code=>{fs.closeSync(fd);state.current={...state.current,exitCode:code};write();code===0?resolve():reject(Error(label+' exit '+code));});});
(async()=>{
 state.status='running';write();
 for(const r of requests){
  const file=path.join(out,r.id+'.gif');state.current={label:r.id+'-download',startedAt:new Date().toISOString()};write();
  if(!fs.existsSync(file)){const response=await fetch(r.url,{signal:AbortSignal.timeout(60000)});if(!response.ok)throw Error('HTTP '+response.status);fs.writeFileSync(file,Buffer.from(await response.arrayBuffer()));}
  else if(!resuming||r.id!=='tsr-disocclusion')throw Error('Unexpected preserved source requires direct diagnosis');
  const probe=spawnSync(ffprobe,['-v','error','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,time_base,nb_frames:format=duration,size','-of','json',file],{encoding:'utf8',windowsHide:true});if(probe.status!==0)throw Error('Probe failed');
  const mp4=path.join(out,r.id+(resuming?'-even-v2':'')+'.mp4');
  // Exactly one native GIF cycle; no looping, slowdown or repeated display time.
  await run(r.id+'-one-cycle'+(resuming?'-v2':''),ffmpeg,['-n','-v','error','-threads','2','-filter_threads','2','-ignore_loop','1','-i',file,'-an','-vf','pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black','-fps_mode','passthrough','-c:v','libx264','-threads','2','-crf','18','-pix_fmt','yuv420p',mp4]);
  const mp=spawnSync(ffprobe,['-v','error','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,time_base,nb_frames:format=duration,size','-of','json',mp4],{encoding:'utf8',windowsHide:true});if(mp.status!==0)throw Error('MP4 probe failed');
  await run(r.id+'-decode',ffmpeg,['-v','error','-threads','2','-i',mp4,'-f','null','-']);
  const record={...r,primary,original:{path:path.relative(root,file).replaceAll('\\','/'),sha256:sha(file),probe:JSON.parse(probe.stdout)},media:path.relative(root,mp4).replaceAll('\\','/'),sha256:sha(mp4),probe:JSON.parse(mp.stdout),wholeDecodeExit:0,oneNativeCycleOnly:true,padding:'At most one black pixel on right/bottom; original content not cropped.',sourceAudioUsed:false,movingPixelsReviewed:false,rightsApproved:false,finalUseApproved:false,localOnly:true};
  state.completed.push(record);state.current=null;write();console.log(JSON.stringify({id:r.id,duration:record.probe.format.duration,finalUseApproved:false}));
 }
 state.status='acquired-one-cycle-native-processes';state.completedAt=new Date().toISOString();state.current=null;write();
})().catch(e=>{state.status='failed';state.error=e.stack;write();console.error(e);process.exitCode=1;});
