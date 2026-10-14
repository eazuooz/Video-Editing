// One closed CPU source render; final pixel/mix gates remain separate.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
process.chdir(path.resolve(__dirname,'../../..'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const base='production/research/game-lighting-history/local/episode04-comparison-clearance-v7',plan=read(base+'/plan.json'),job=plan.jobs.find(j=>j.name===process.argv[2]);
if(!job)throw Error('Exact prepared job required');
const out=job.output.replace(/\.mp4$/,'.verification.json');if(fs.existsSync(out))throw Error('Preserve observed verification');
const execution=read(job.execution);if(execution.status!=='complete'||execution.exitCode!==0||!fs.existsSync(job.output))throw Error('Actual completed source render required');
const bin='C:/ProgramData/HP/LCDDisplayHelper/bin/',run=(exe,args)=>{const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr||'Command failed');return r.stdout;};
const live=run('powershell.exe',['-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'ffmpeg.exe' -and $_.CommandLine -match 'game-lighting-history' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"]);if(live.trim())throw Error('Another owned media worker live');
if(sha(plan.runtime.path)!==plan.runtime.sha256||sha(job.audio.path)!==job.audio.sha256)throw Error('Prepared runtime/PCM changed');
const probe=JSON.parse(run(bin+'ffprobe.exe',['-v','error','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,nb_frames,sample_rate,channels,duration:format=duration,size','-of','json',job.output])),video=probe.streams.find(s=>s.codec_type==='video'),audio=probe.streams.find(s=>s.codec_type==='audio');
if(video.width!==1920||video.height!==1080||video.r_frame_rate!=='60/1'||video.time_base!=='1/90000'||+video.nb_frames!==job.frames||Math.abs(+video.duration-job.frames/60)>0.000002||audio.codec_name!=='aac'||audio.sample_rate!=='24000'||audio.channels!==1)throw Error('Encoded source metadata mismatch');
const packets=JSON.parse(run(bin+'ffprobe.exe',['-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration','-of','json',job.output])).packets.sort((a,b)=>a.pts-b.pts);
if(packets.length!==job.frames||packets.some((p,i)=>p.pts!==i*1500||p.duration!==1500))throw Error('Continuous90000/60 presentation clock required');
run(bin+'ffmpeg.exe',['-v','error','-threads','2','-i',job.output,'-f','null','-']);
const record={verifiedAt:new Date().toISOString(),scope:'Complete clean explanation source only, not approval of final mixture/interleaving/pixels/private',execution:{path:job.execution,sha256:sha(job.execution),observedExitCode:0},media:{path:job.output,sha256:sha(job.output),bytes:fs.statSync(job.output).size},probe,frames:job.frames,packetCount:packets.length,allPacketPtsAndDurationsApproved:true,ptsStep:1500,timeBase:'1/90000',wholeDecodeExitCode:0,unchangedPreparedPcm:job.audio,scenes:job.scenes,allSourceEncodedPixelsReviewed:false,sceneBoundaryPixelsApproved:false,finalAllPixelsReviewed:false,finalMixedAsrApproved:false,humanListeningApproved:false,newGitImages:0};
fs.writeFileSync(out,JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({name:job.name,frames:job.frames,decode:0,pts:true,sha256:record.media.sha256,allPixelsReviewed:false}));
