// Encode only the frozen, directly reviewed actual-game selection. CPU only.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',probe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),rel=p=>path.relative(root,p).replaceAll('\\','/'),abs=p=>path.join(root,p);
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
async function hash(p){const h=crypto.createHash('sha256');for await(const chunk of fs.createReadStream(p))h.update(chunk);return h.digest('hex');}
const plan=read(path.join(work,'plan.json')),selection=read(path.join(work,'cut-selection.json')),processes=[];
const stateFile=path.join(work,'source-compile-execution.json'),qpath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
function save(status,child=null){const state={pid:process.pid,status,updatedAt:new Date().toISOString(),child,processes,sourceAudioStreams:0,finalVideoApproved:false};write(stateFile,state);const q=read(qpath),item=q.items.find(x=>x.slug==='hierarchical-game-outlines');item.execution.sourceCompile=state;item.execution.activeTasks=status==='actual-source-cpu-encoding'?[{kind:'actual-source-cpu-encoding',pid:process.pid,childPid:child?.pid??null,state:rel(stateFile)}]:[];item.execution.status=status;item.updatedAt=state.updatedAt;write(qpath,q);}
async function run(cmd,args,log,kind){return new Promise((resolve,reject)=>{const fd=fs.openSync(log,'w'),child=spawn(cmd,args,{cwd:root,stdio:['ignore',fd,fd],windowsHide:true});save('actual-source-cpu-encoding',{pid:child.pid,kind,log:rel(log),command:[cmd,...args]});child.on('error',reject);child.on('exit',code=>{fs.closeSync(fd);processes.push({pid:child.pid,exitCode:code,kind,log:rel(log),command:[cmd,...args]});if(code!==0)reject(Error(`${kind} failed:${code}; inspect ${rel(log)}`));else resolve(fs.readFileSync(log,'utf8'));});});}
async function inspect(file,frames,tag){const text=await run(probe,['-v','error','-show_streams','-of','json',file],path.join(work,tag+'-probe.json'),tag+'-probe'),p=JSON.parse(text),v=p.streams.find(s=>s.codec_type==='video');
 if(!v||p.streams.some(s=>s.codec_type==='audio')||+v.nb_frames!==frames||v.width!==1920||v.height!==1080||v.avg_frame_rate!=='60/1')throw Error('Actual-media frame/audio/layout mismatch:'+tag);
 await run(ff,['-v','error','-threads','2','-i',file,'-map','0:v:0','-f','null','-'],path.join(work,tag+'-decode.log'),tag+'-decode');
 return {file:rel(file),frames,width:v.width,height:v.height,fps:v.avg_frame_rate,audioStreams:0,sha256:await hash(file),wholeDecodeExitCode:0};}
(async()=>{
 if(process.argv.includes('--inspect')){console.log(JSON.stringify({sourceRevision:selection.sourceLayoutRevision,cuts:selection.cuts.length,actualTargetSeconds:plan.gameplaySeconds,explanationTargetSeconds:plan.explanationSeconds,sourceGateExists:fs.existsSync(path.join(work,'final-source-cut-review.json')),finalVideoApproved:false}));return;}
 const gate=read(path.join(work,'final-source-cut-review.json')),voice=read(path.join(__dirname,'voice-approval-v2.json'));
 if(!gate.approved||gate.selectionSha256!==await hash(path.join(work,'cut-selection.json'))||gate.layoutSha256!==await hash(path.join(work,'caption-layout-qa.json'))||!gate.allCurrentActualCaptionSegmentsDirectlyReviewed||!gate.allNativeBoundariesDirectlyReviewed)throw Error('Current precise source/caption review required before encoding.');
 if(!voice.allCurrentScenesTechnicallyReviewed||!voice.all60ParagraphsDirectlyCompared||!voice.unchangedPcmVerified)throw Error('Current whole voice and retained PCM review required.');
 if(fs.existsSync(stateFile))throw Error('Inspect existing source compilation; never overwrite or duplicate it.');
 if(selection.sourceLayoutRevision!=='v3'||selection.cuts.some(c=>c.composition.mode!=='full-screen-face-free-game-crop'||c.speed!==1||c.loop||c.sourceId!=='I-ccSZ5J1Bo'))throw Error('Normal full-screen existing-game selection required.');
 if(selection.sourceSha256!==await hash(abs(selection.cuts[0].file)))throw Error('Actual source bytes changed.');
 for(const s of plan.scenes)if(await hash(abs(s.voice))!==s.audioSha256)throw Error('Current approved voice changed:'+s.id);
 if(selection.cuts.reduce((n,c)=>n+c.frames,0)!==plan.actualFrames||Math.abs(plan.actualFrames-.6*plan.bodyFrames)>1)throw Error('Exact frame targets changed.');
 save('actual-source-cpu-encoding');
 const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
 const compiled=[];
 for(const s of plan.scenes.filter(s=>s.classification==='actual')){
  const files=[];
  for(const c of s.cuts){
   const file=path.join(work,`cut-${c.id}.mp4`),label=path.join(work,`source-label-${c.id}.txt`);if(fs.existsSync(file))throw Error('Preserve existing cut:'+c.id);
   write(label,'Two Point Museum · 공식 시연 / 추가 콘텐츠 미리보기 (2026)');
   const labelPath=rel(label).replaceAll(':','\\:');
   const vf=`crop=1376:774:0:0,scale=1920:1080,setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${labelPath}':fontsize=22:fontcolor=0x073c32:x=19:y=7:box=1:boxcolor=white@0.92:boxborderw=7`;
   await run(ff,['-hide_banner','-threads','2','-ss',String(c.sourceIn),'-t',String(c.seconds),'-i',abs(c.file),'-map','0:v:0','-frames:v',String(c.frames),'-vf',vf,...enc,file],path.join(work,`cut-${c.id}-encode.log`),'cut-'+c.id);
   const verified=await inspect(file,c.frames,'cut-'+c.id);c.encodedVideo=rel(file);c.encodedVerification=verified;files.push(file);compiled.push(verified);
  }
  const list=path.join(work,`actual-scene-${s.id}-concat.txt`);write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
  const file=abs(`shared/output/hierarchical-game-outlines/actual-scenes/scene${s.id}.mp4`);if(fs.existsSync(file))throw Error('Preserve existing chapter:'+s.id);fs.mkdirSync(path.dirname(file),{recursive:true});
  await run(ff,['-v','error','-f','concat','-safe','0','-i',list,'-an','-c:v','copy','-movflags','+faststart',file],path.join(work,`actual-scene-${s.id}-concat.log`),'concat-'+s.id);
  s.actualVideo=rel(file);s.actualMediaVerified=await inspect(file,s.frames,'actual-scene-'+s.id);
  write(path.join(work,'source-compile-progress.json'),{updatedAt:new Date().toISOString(),compiled,captionsApprovedForFinal:false,finalVideoApproved:false});
 }
 plan.finalSourceTimingApproved=true;plan.actualFootageMeasuredAndApproved=true;plan.captionReviewComplete=false;plan.timingStatus='exact audio-free actual chapters measured; encoded boundary and full final pixel QA pending';
 write(path.join(work,'plan.json'),plan);write(path.join(work,'actual-media-review.json'),{createdAt:new Date().toISOString(),cuts:compiled,actualFrames:plan.actualFrames,actualSeconds:plan.gameplaySeconds,explanationFrames:plan.explanationFrames,ratioErrorFrames:Math.abs(plan.actualFrames-.6*plan.bodyFrames),selfCreatedGames:0,sourceAudioStreams:0,allEncodedNativeBoundaryPixelsReviewed:false,allFinalCaptionPixelsReviewed:false,finalVideoApproved:false});
 save('actual-source-compiled-encoded-visual-review-pending');console.log('Six actual chapters measured; encoded and final caption QA remain pending.');
})().catch(e=>{if(fs.existsSync(stateFile))save('actual-source-compile-failed');console.error(e.message);process.exitCode=1;});
