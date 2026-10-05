// CPU-only native review files, one child at a time; no final render or source audio.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'measured-edit-v3'),dest=path.join(work,'native-review-v3');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,'')),rel=p=>path.relative(root,p).replaceAll('\\','/');
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const stamp=()=>new Date().toISOString(),pause=ms=>Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,ms);
const write=(p,d)=>{const tmp=p+'.'+process.pid+'.writing';for(let k=0;;k++){try{fs.writeFileSync(tmp,JSON.stringify(d,null,2)+'\n');fs.renameSync(tmp,p);return;}catch(e){if(k>=30||!['UNKNOWN','EPERM','EBUSY','EACCES'].includes(e.code))throw e;pause(100);}}};
async function sha(p){const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(p))h.update(b);return h.digest('hex');}
const planFile=path.join(work,'plan.json'),plan=read(planFile),cuts=plan.scenes.flatMap(s=>s.segments.filter(c=>c.classification==='actual-existing-game').map(c=>({...c,sceneId:s.id})));
if(cuts.length!==85||plan.finalTimingApproved||cuts.some(c=>c.speed!==1||c.sourceAudioStreams!==0))throw Error('Unapproved current13 guided60 native candidate expected.');
const resume=false;
const previousFile=path.join(__dirname,'measured-edit-v2/native-review-v1/compiled.json');
const previous=read(previousFile);
if(read(path.join(__dirname,'measured-edit-v2/native-review-v1/execution.json')).exitCode!==0)throw Error('Observed closed v2 completion required.');
if(fs.existsSync(dest)&&!resume)throw Error('Preserve the current compiler and inspect its actual completion before continuing.');
if(!fs.existsSync(dest))fs.mkdirSync(dest);
const state={schemaVersion:1,status:'native-review-cpu-compiling',startedAt:stamp(),pid:process.pid,sessionId:null,
 threads:2,gpuJobs:0,activeTasks:[],completed:[],processes:[],totalCuts:cuts.length,
 finalApproved:false,allCaptionPixelsReviewed:false,encodedBoundaryPixelsReviewed:false,reusedCuts:0,newEncodedCuts:0,previousCompiled:rel(previousFile)};
if(resume){const old=read(path.join(dest,'execution.json'));if(old.exitCode!==1||!old.endedAt||old.activeTasks.length)throw Error('Directly observed closed failed compiler required.');state.history=[old];state.completed=old.completed;state.processes=old.processes;state.recovery='Atomic Windows metadata write/retry; all completed files reused by exact hash. Unregistered complete encode adopted only after probe/decode, with its original exit code left unobserved.';}
function save(){
 const sessionFile=path.join(dest,'session.json');if(fs.existsSync(sessionFile)){const s=read(sessionFile);if(s.pid===state.pid)state.sessionId=s.sessionId;}
 state.updatedAt=stamp();write(path.join(dest,'execution.json'),state);
 const qfile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),q=read(qfile),i=q.items.find(x=>x.slug==='making-game-sequels');
 i.stage='current13-guided60-native-v3-only-changed-cuts-compilation';
 i.execution={...i.execution,phase:i.stage,status:state.status,pid:state.pid,sessionId:state.sessionId,alive:!state.endedAt,
  commandLine:'node projects/making-game-sequels/production/compile-native-candidate-v3.cjs',activeTasks:state.activeTasks,
  state:rel(path.join(dest,'execution.json')),cpuProductionJobs:state.endedAt?0:1,gpuSynthesisJobs:0,renderJobs:0,uploads:0,
  nativeReviewCompile:{completedCuts:state.completed.length,totalCuts:cuts.length}};
 i.measuredEditCandidate={path:rel(planFile),actualFrames:plan.actualFrames,explanationFrames:plan.explanationFrames,
  finalFrames:plan.finalFrames,ratioErrorFrames:plan.ratioRoundingErrorFrames,allCurrentPcmPreserved:true,
  finalTimingApproved:false,bodyRatioApproved:false};
 i.nextAction='Inspect new native boundaries and every changed guide/caption against current words; preserve all554.584s component PCM and original white explanations. Final pixels/new joins/mix/timing remain pending.';
 i.updatedAt=stamp();q.updatedAt=i.updatedAt;write(qfile,q);
 const cpfile=path.join(__dirname,'latest-checkpoint.json'),cp=read(cpfile);
 Object.assign(cp,{stage:i.stage,updatedAt:i.updatedAt,execution:i.execution,nextAction:i.nextAction,measuredEditCandidate:i.measuredEditCandidate});write(cpfile,cp);
}
async function run(exe,args,id){
 const log=path.join(dest,id+'.log');
 return new Promise((resolve,reject)=>{
  const fd=fs.openSync(log,'w'),child=spawn(exe,args,{cwd:root,stdio:['ignore',fd,fd],windowsHide:true});
  state.activeTasks=[{pid:child.pid,command:[exe,...args],log:rel(log)}];save();
  child.once('error',e=>{fs.closeSync(fd);reject(e);});
  child.once('exit',code=>{fs.closeSync(fd);state.processes.push({pid:child.pid,kind:id,exitCode:code,log:rel(log)});state.activeTasks=[];save();
   if(code!==0)reject(Error(id+' exited '+code));else resolve(fs.readFileSync(log,'utf8'));});
 });
}
(async()=>{
 state.planSha256=await sha(planFile);save();state.sources=[];
 for(const a of plan.assets){if(await sha(path.join(root,a.source))!==a.sourceSha256)throw Error('Source hash changed '+a.assetId);state.sources.push({assetId:a.assetId,path:a.source,sha256:a.sourceSha256});}
 save();
 for(const c of cuts){
  const prior=state.completed.find(x=>x.id===c.id);
  if(prior){if(await sha(path.join(root,prior.video))!==prior.sha256||prior.frames!==c.frames)throw Error('Preserved compiled cut changed '+c.id);continue;}
  const reusable=previous.cuts.find(x=>x.assetId===c.assetId&&x.sourceStartFrame===c.sourceStartFrame&&x.sourceEndFrameExclusive===c.sourceEndFrameExclusive&&x.nativeFps===c.nativeFps&&x.frames===c.frames);
  if(reusable){
   if(reusable.audioStreams!==0||reusable.wholeDecodeExitCode!==0||reusable.wholeDecodeDiagnostics!==0||await sha(path.join(root,reusable.video))!==reusable.sha256)throw Error('Reused native cut evidence/hash changed '+c.id);
   state.completed.push({...reusable,id:c.id,sceneId:c.sceneId,startFrame:c.startFrame,previousId:reusable.id,
    byteIdenticalPreviousCompileReused:true,reuseReviewedAt:stamp(),previousCompiledSha256:await sha(previousFile),
    finalApproved:false,allCaptionPixelsApproved:false,composition:{...reusable.composition,finalFramingApproved:false,
     proposedCrop:c.bankCutId===28?[0,252,1472,828]:c.bankCutId===49?[192,270,1056,594]:reusable.composition.proposedCrop}});
   state.reusedCuts++;write(path.join(dest,'compiled.json'),{schemaVersion:1,status:'native-review-only',planSha256:state.planSha256,sources:state.sources,cuts:state.completed,finalApproved:false});
   save();console.log(`Byte-identical native review reuse ${state.completed.length}/${cuts.length}: ${c.id}`);continue;
  }
  const start=c.sourceStartFrame/c.nativeFps,end=c.sourceEndFrameExclusive/c.nativeFps,seek=Math.max(0,Math.floor(start)-1),file=path.join(dest,c.id+'.mp4');
  // Bound input decoding before selection; exact PTS trim, normal-speed native
  // frames, standard30→60 duplication only. Never loop or interpolate motion.
  const vf=`trim=start=${(start-.000001).toFixed(9)}:end=${(end-.000001).toFixed(9)},setpts=PTS-STARTPTS,fps=60:round=near,trim=end_frame=${c.frames},setsar=1`;
  const existingUnregistered=fs.existsSync(file);
  if(existingUnregistered&&!resume)throw Error('Unexpected existing unregistered encode '+c.id);
  if(!existingUnregistered)await run(ff,['-v','error','-nostdin','-threads','2','-filter_threads','1','-copyts','-ss',String(seek),'-t',String(end-seek+.1),
   '-i',path.join(root,c.source),'-map','0:v:0','-vf',vf,'-frames:v',String(c.frames),'-an','-c:v','libx264','-threads','2',
   '-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',file],c.id+'-encode');
  const streams=JSON.parse(await run(fp,['-v','error','-show_streams','-of','json',file],c.id+'-probe')).streams,v=streams.find(x=>x.codec_type==='video');
  if(!v||+v.nb_frames!==c.frames||v.avg_frame_rate!=='60/1'||v.width!==1920||v.height!==1080||streams.some(x=>x.codec_type==='audio'))throw Error('Native layout/frame/audio mismatch '+c.id);
  const diagnostics=await run(ff,['-v','error','-threads','2','-i',file,'-map','0:v:0','-f','null','-'],c.id+'-decode');
  if(diagnostics.trim())throw Error('Whole-cut decode diagnostics '+c.id);
  state.completed.push({id:c.id,sceneId:c.sceneId,assetId:c.assetId,videoId:c.videoId,sourceStartFrame:c.sourceStartFrame,
   sourceEndFrameExclusive:c.sourceEndFrameExclusive,nativeFps:c.nativeFps,frames:c.frames,startFrame:c.startFrame,
   video:rel(file),sha256:await sha(file),audioStreams:0,wholeDecodeExitCode:0,wholeDecodeDiagnostics:0,
   encodeExitCode:existingUnregistered?null:0,unregisteredCompletedEncodeReused:existingUnregistered,
   encodeCompletionBasis:existingUnregistered?'Original child no longer alive; preserved complete file passed frame/layout/audio probe and whole decode. Original encode exit was not observed.':'Actual child exit0 observed.',
   finalApproved:false,allCaptionPixelsApproved:false,encodedBoundaryPixelsReviewed:false,
   composition:{mode:'full-screen-native-review-before-final-framing',finalFramingApproved:false,
    proposedCrop:c.bankCutId===49?[192,270,1056,594]:c.videoId==='MXxOg1xuWcI'?[192,0,1536,864]:c.videoId==='kzZI_mbp0HY'?[0,0,1472,828]:[0,0,1920,1080]}});
  state.newEncodedCuts++;
  write(path.join(dest,'compiled.json'),{schemaVersion:1,status:'native-review-only',planSha256:state.planSha256,sources:state.sources,cuts:state.completed,finalApproved:false});
  save();console.log(`Native review ${state.completed.length}/${cuts.length}: ${c.id}`);
 }
 state.status='native-review-compiled-all-cues-framing-and-boundaries-pending';state.endedAt=stamp();state.exitCode=0;save();
})().catch(e=>{state.status='native-review-compile-failed';state.error=String(e);state.activeTasks=[];state.endedAt=stamp();state.exitCode=1;save();console.error(e);process.exitCode=1;});
