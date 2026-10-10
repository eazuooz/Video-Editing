// Preserve v4/chapter bitstreams and AAC; correct only observed container timestamp rounding.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),rel='production/research/game-lighting-history/local/episode03-chapter-render-v4',read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),plan=read(rel+'/plan.json');
const source=rel+'/all14-chapters.captioned.mp4',out=rel+'/all14-chapters-pts-v5.captioned.mp4',statePath=rel+'/assembly-execution-v5.json',ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
if(fs.existsSync(path.join(root,out))||fs.existsSync(path.join(root,statePath)))throw Error('Existing v5 state preserved');
if(read(rel+'/assembly-execution-v4.json').error!=='Error: Joined PTS not continuous')throw Error('Diagnosed v4 failure required');
const run=(exe,args)=>{const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:80*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;};
if(run('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CreationDate,CommandLine | ConvertTo-Json -Compress"]).trim())throw Error('Owned media job still active');
for(const i of plan.inputs)if(sha(i.path)!==i.sha256)throw Error('Frozen input changed');
const packets=p=>JSON.parse(run(fp,['-v','error','-show_packets','-show_data_hash','sha256','-show_entries','packet=stream_index,pts,dts,duration,size,data_hash','-of','json',path.join(root,p)])).packets;
const old=packets(source),video=old.filter(p=>p.stream_index===0),pts=video.map(p=>p.pts).sort((a,b)=>a-b),errors=pts.map((p,i)=>p-i*1500);
if(pts.length!==plan.frames||errors.some(x=>Math.abs(x)>=750)||!errors.some(x=>x))throw Error('Expected only sub-half-frame timestamp rounding');
const createdAt=new Date().toISOString(),state=o=>fs.writeFileSync(path.join(root,statePath),JSON.stringify({createdAt,pid:process.pid,command:process.argv,cwd:root,cpuThreads:2,gpuJobs:0,finalVideo:false,...o},null,2)+'\n');
try{
 const args=['-v','error','-nostdin','-threads','2','-i',path.join(root,source),'-map','0','-c','copy','-bsf:v','setts=pts=round(PTS/1500)*1500:dts=round(DTS/1500)*1500:duration=1500','-video_track_timescale','90000','-movflags','+faststart',path.join(root,out)];
 state({status:'running',step:'timestamp-only-remux',childCommand:[ff,...args]});run(ff,args);
 const current=packets(out),newPts=current.filter(p=>p.stream_index===0).map(p=>p.pts).sort((a,b)=>a-b);
 if(newPts.length!==plan.frames||newPts.some((p,i)=>p!==i*1500))throw Error('Recovered timestamps still differ');
 const payload=p=>JSON.stringify(p.map(x=>({stream:x.stream_index,size:x.size,sha256:x.data_hash})));
 if(payload(old)!==payload(current))throw Error('Video/AAC compressed payload changed');
 const probe=JSON.parse(run(fp,['-v','error','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_read_frames,duration,sample_rate,channels','-of','json',path.join(root,out)]));
 const v=probe.streams.find(s=>s.codec_type==='video'),a=probe.streams.find(s=>s.codec_type==='audio');if(v.time_base!=='1/90000'||v.r_frame_rate!=='60/1'||Number(v.nb_read_frames)!==plan.frames||Math.abs(Number(a.duration)-plan.audio.durationSeconds)>.03)throw Error('Frame/audio probe differs');
 state({status:'running',step:'whole-decode',childCommand:[ff,'-v','error','-threads','2','-i',path.join(root,out),'-f','null','NUL']});run(ff,['-v','error','-threads','2','-i',path.join(root,out),'-f','null','NUL']);
 const record={completedAt:new Date().toISOString(),scope:plan.scope,source:{path:source,sha256:sha(source),failedExecution:rel+'/assembly-execution-v4.json',observedPtsErrors:[...new Set(errors)]},video:{path:out,sha256:sha(out),probe},plan:{path:rel+'/plan.json',sha256:sha(rel+'/plan.json')},originalPCM:plan.audio,originalPcmByteIdentical:sha(plan.audio.path)===plan.audio.sha256,observedFrames:newPts.length,firstPts:0,lastPts:newPts.at(-1),timebase:90000,allPresentationPtsContinuous:true,compressedVideoAndAacPacketsIdentical:true,compressedPayloadSha256:crypto.createHash('sha256').update(payload(current)).digest('hex'),wholeDecode:{exitCode:0},remuxCommand:[ff,...args],primaryReference:'https://ffmpeg.org/ffmpeg-bitstream-filters.html#setts',allPixelsReviewed:false,finalEpisodeApproved:false,localOnly:true};
 fs.writeFileSync(path.join(root,rel+'/assembly-verification-v5.json'),JSON.stringify(record,null,2)+'\n');state({status:'complete-awaiting-direct-pixel-review',exitCode:0,completedAt:record.completedAt});console.log(JSON.stringify({frames:newPts.length,exactPts:true,identicalVideoAacPayload:true,decode:0,finalEpisode:false}));
}catch(e){state({status:'failed-preserve-v4-v5-and-chapters',error:String(e)});throw e;}
