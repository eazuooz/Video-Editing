const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),b='production/research/game-lighting-history/local/episode03-native-v5',out=path.join(root,b),py=path.join(root,'qwen3-tts/.venv/Scripts/python.exe'),ffmpeg='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const sources=[
  {
    "id": "vnpUykzHpv8",
    "slug": "nvrtx-showcase-2021",
    "primary": "https://developer.nvidia.com/blog/try-nvidia-game-development-sdks-in-the-interactive-rtx-technology-showcase/",
    "chapter": "13b/15a/15b UE4.26 actual SDK toggles; separate DDGI/direct light/reflection inputs"
  },
  {
    "id": "0X1RtXCvPFQ",
    "slug": "dlss2-overview-2020",
    "primary": "https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/",
    "chapter": "14b actual game temporal image comparisons; exclude product cards and diagrams from actual quota"
  },
  {
    "id": "via-LSKo_q4",
    "slug": "deliver-moon-dlss2-2020",
    "primary": "https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/",
    "chapter": "14b native lower-resolution reconstruction comparison"
  },
  {
    "id": "1fSx2VBHKz0",
    "slug": "wolfenstein-dlss2-2020",
    "primary": "https://www.nvidia.com/en-us/geforce/news/nvidia-dlss-2-0-a-big-leap-in-ai-rendering/",
    "chapter": "14a/14b ray effects and temporal reconstruction, source version2020"
  },
  {
    "id": "ycNk1nj0KsQ",
    "slug": "rtxgi-ue5-preview2-2022",
    "primary": "https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/",
    "chapter": "15a DDGI actual volume placement/debug controls; exclude installation/file dialogs and static explanatory slides"
  },
  {
    "id": "49rBP1DoOwo",
    "slug": "hardware-rt-ue5-preview2-2022",
    "primary": "https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/",
    "chapter": "13a/13b actual engine RT enable/debug settings; exclude installation and prose cards"
  },
  {
    "id": "Xk15X9ab7iw",
    "slug": "dlss-ue5-preview2-2022",
    "primary": "https://developer.nvidia.com/blog/shaping-the-future-of-graphics-with-nvidia-technologies-in-unreal-engine-5/",
    "chapter": "14b actual viewport reconstruction setting comparison; DLSS/DLAA/NIS distinct"
  }
];
const guard=spawnSync('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"],{encoding:'utf8',windowsHide:true});if(guard.status!==0||guard.stdout.trim())throw Error('Owned single media slot busy');
const gpu=spawnSync('nvidia-smi',['--query-gpu=memory.used,memory.total,utilization.gpu','--format=csv,noheader'],{encoding:'utf8',windowsHide:true});if(gpu.status!==0)throw Error('Resource observation failed');
fs.mkdirSync(out,{recursive:true});const statePath=path.join(out,'execution.json'),startedAt=new Date().toISOString();let completed=[],failures=[],current=null;
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=x=>fs.writeFileSync(statePath,JSON.stringify({startedAt,parentPid:process.pid,command:process.argv,cwd:root,cpuThreads:2,gpuJobs:0,gpuObserved:gpu.stdout.trim(),completed,failures,current,finalUseApproved:false,...x},null,2)+'\n');
const run=(label,exe,args)=>new Promise((resolve,reject)=>{const log=fs.openSync(path.join(out,label+'.log'),'a'),child=spawn(exe,args,{cwd:root,windowsHide:true,env:{...process.env,OMP_NUM_THREADS:'2'},stdio:['ignore',log,log]});current={label,pid:child.pid,executable:exe,args,startedAt:new Date().toISOString()};write({status:'running'});child.on('error',e=>{fs.closeSync(log);reject(e)});child.on('close',code=>{fs.closeSync(log);current={...current,exitCode:code,endedAt:new Date().toISOString()};write({status:code===0?'step-complete':'step-failed'});code===0?resolve():reject(Error(label+' actual exit'+code));});});
(async()=>{for(const s of sources){try{const file=path.join(out,s.slug+'.mp4'),meta=path.join(out,s.slug+'.info.json'),evidence=path.join(out,s.slug+'.acquisition.json');if(fs.existsSync(evidence)){completed.push(JSON.parse(fs.readFileSync(evidence)));continue;}
 if(!fs.existsSync(file)||!fs.existsSync(meta))await run(s.slug+'-download',py,['-X','utf8','-m','yt_dlp','--no-progress','--http-chunk-size','1M','--no-playlist','--no-overwrites','--write-info-json','--no-write-thumbnail','--js-runtimes','node:'+process.execPath,'--retries','2','--fragment-retries','2','--socket-timeout','30','-f','bv*[height<=1080][ext=mp4][vcodec^=avc]/bv*[height<=1080][ext=mp4]','-o',path.join(out,s.slug+'.%(ext)s'),'https://www.youtube.com/watch?v='+s.id]);
 const info=JSON.parse(fs.readFileSync(meta,'utf8')),probe=JSON.parse(spawnSync(ffprobe,['-v','error','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,time_base,nb_frames:format=duration,size','-of','json',file],{encoding:'utf8',windowsHide:true}).stdout);if(probe.streams.some(x=>x.codec_type==='audio'))throw Error('Video-only acquisition required');
 await run(s.slug+'-whole-decode',ffmpeg,['-v','error','-threads','2','-i',file,'-f','null','-']);
 const dir=path.join(out,s.slug+'-review');fs.mkdirSync(dir,{recursive:true});const samples=Math.ceil(Number(probe.format.duration)/5);
 await run(s.slug+'-samples',ffmpeg,['-v','error','-threads','2','-i',file,'-vf',"fps=1/5,scale=640:360,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='%{pts\\:hms}':x=8:y=8:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.8,tile=3x2:nb_frames=6:padding=4:margin=4",'-vsync','0','-threads','2',path.join(dir,'board-%03d.png')]);
 const record={...s,url:'https://www.youtube.com/watch?v='+s.id,title:info.title,publisher:info.channel,channelId:info.channel_id,uploadDate:info.upload_date,media:path.relative(root,file).replaceAll('\\','/'),sha256:sha(file),probe,wholeDecodeExit:0,sourceAudioAcquired:false,sampleSpacingSeconds:5,plannedSampleCount:samples,boards:fs.readdirSync(dir).filter(x=>/^board-\d+\.png$/.test(x)).map(x=>({path:path.relative(root,path.join(dir,x)).replaceAll('\\','/'),sha256:sha(path.join(dir,x)),directlyViewed:false})),rightsApproved:false,recentUseCheckPassed:false,fullMotionReviewed:false,finalUseApproved:false,acquiredAt:new Date().toISOString(),localOnly:true};fs.writeFileSync(evidence,JSON.stringify(record,null,2)+'\n');completed.push(record);current=null;write({status:'source-complete'});console.log(JSON.stringify({source:s.slug,duration:probe.format.duration,boards:record.boards.length}));}catch(e){failures.push({source:s.slug,error:e.message,observedAt:new Date().toISOString(),noAuthenticationOrAccessBypass:true});console.log(JSON.stringify(failures.at(-1)));current=null;write({status:'source-failed-continuing-independent-sources'});}}
 write({status:failures.length?'partial-native-and-samples-ready':'native-and-samples-ready',completedAt:new Date().toISOString(),next:'Directly read every board, review selected transitions and source rights/recent use; no final seconds approved by acquisition.'});})().catch(e=>{write({status:'failed',error:e.stack});console.error(e);process.exitCode=1;});
