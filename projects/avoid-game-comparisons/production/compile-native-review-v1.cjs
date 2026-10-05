// Compile only the frozen native action candidate for later pixel/caption review.
// Each source interval plays once at normal speed. This is not a final video.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawn}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const measuredV6=process.argv.includes('--measured-v6');
const measuredV5=process.argv.includes('--measured-v5')||measuredV6;
const measuredV4=process.argv.includes('--measured-v4')||measuredV5;
const measuredV3=process.argv.includes('--measured-v3')||measuredV4;
const measuredV2=process.argv.includes('--measured-v2')||measuredV3;
const work=path.join(__dirname,measuredV6?'measured-edit-v6':measuredV5?'measured-edit-v5':measuredV4?'measured-edit-v4':measuredV3?'measured-edit-v3':measuredV2?'measured-edit-v2':'measured-edit-v1'),dest=path.join(work,'native-review-v1');
const planPath=path.join(work,'plan.json');
const sourceDir=path.join(root,'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons/research-local/game-sources');
const queuePath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
const checkpointPath=path.join(__dirname,'latest-checkpoint.json');
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';
const fp='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const pause=ms=>Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,ms);
const write=(p,d)=>{const temp=p+'.'+process.pid+'.writing';
 for(let attempt=0;;attempt++){
  try{fs.writeFileSync(temp,JSON.stringify(d,null,2)+'\n');fs.renameSync(temp,p);return;}
  catch(e){if(attempt>=20||!['EPERM','EBUSY','EACCES'].includes(e.code))throw e;pause(100);}
 }
};
async function sha(p){const h=crypto.createHash('sha256');for await(const b of fs.createReadStream(p))h.update(b);return h.digest('hex');}
const plan=read(planPath);
const cuts=plan.scenes.flatMap(s=>s.segments.filter(c=>c.classification==='actual-existing-game').map(c=>({...c,sceneId:s.id})));
if(cuts.length!==(measuredV5?111:measuredV2?108:105)||plan.finalTimingApproved||cuts.some(c=>c.speed!==1||c.sourceAudioStreams!==0))throw Error('Unexpected native candidate.');
const resume=process.argv.includes('--resume-observed-exit1');
if(fs.existsSync(dest)&&!resume)throw Error('Preserve the existing native compiler; inspect execution before any continuation.');
if(!fs.existsSync(dest))fs.mkdirSync(dest);
const state={schemaVersion:1,status:'native-source-review-cpu-compiling',startedAt:new Date().toISOString(),
 pid:process.pid,sessionId:null,threads:2,gpuJobs:0,activeTasks:[],completed:[],processes:[],
 totalCuts:cuts.length,finalApproved:false,allCaptionPixelsReviewed:false,encodedBoundaryPixelsReviewed:false};
if(resume){
 const old=read(path.join(dest,'execution.json'));
 if(old.exitCode!==1||!old.endedAt||old.activeTasks.length)throw Error('A directly observed closed failed worker is required.');
 state.history=[old];state.completed=old.completed;state.processes=old.processes;
 state.recovery='Normal atomic-write EPERM retry added. Reuse all hash-verified completed cuts; only continue the unfinished candidate.';
}
function save(){
 const sessionFile=path.join(dest,'session.json');if(fs.existsSync(sessionFile)){const sess=read(sessionFile);if(sess.pid===process.pid)state.sessionId=sess.sessionId;}
 state.updatedAt=new Date().toISOString();write(path.join(dest,'execution.json'),state);
 const q=read(queuePath),i=q.items.find(x=>x.slug==='avoid-game-comparisons');
 i.stage='current15-integer-frame-candidate-native-review-compilation';
 i.execution={...i.execution,observedAt:state.updatedAt,phase:i.stage,status:state.status,pid:state.pid,alive:!state.endedAt,
  activeTasks:state.activeTasks,gpuSynthesisJobs:0,cpuProductionJobs:state.endedAt?0:1,renderJobs:0,uploads:0,
  nativeReviewCompile:{pid:state.pid,sessionId:state.sessionId,state:rel(path.join(dest,'execution.json')),completedCuts:state.completed.length,totalCuts:cuts.length}};
 i.nextAction='Inspect all new encoded native boundaries and fixed-caption pixels; resolve12p1 word/action timing before final timing or ratio approval. Preserve all current PCM and original six explanations.';
 i.updatedAt=state.updatedAt;q.updatedAt=state.updatedAt;write(queuePath,q);
 const cp=read(checkpointPath);cp.stage=i.stage;cp.updatedAt=state.updatedAt;cp.execution=i.execution;cp.nextAction=i.nextAction;
 cp.measuredEditCandidate={path:rel(planPath),actualFrames:plan.actualFrames,explanationFrames:plan.explanationFrames,
  finalFrames:plan.finalFrames,ratioErrorFrames:plan.body60_40ErrorFrames,allCurrentPcmPreserved:true,finalTimingApproved:false,bodyRatioApproved:false};
 cp.newDiagramLookdev={path:'projects/avoid-game-comparisons/production/new-diagram-lookdev-review.json',layoutsReviewed:8,finalCuePixelsApproved:false};
 cp.finalVideoComplete=false;write(checkpointPath,cp);
}
async function run(exe,args,id){
 const log=path.join(dest,id+'.log');
 return new Promise((resolve,reject)=>{
  const fd=fs.openSync(log,'w');const child=spawn(exe,args,{cwd:root,stdio:['ignore',fd,fd],windowsHide:true});
  state.activeTasks=[{kind:'native-review-cpu',pid:process.pid,childPid:child.pid,command:[exe,...args],log:rel(log)}];save();
  child.once('error',e=>{fs.closeSync(fd);reject(e);});
  child.once('exit',code=>{fs.closeSync(fd);state.processes.push({kind:id,pid:child.pid,exitCode:code,log:rel(log)});
   state.activeTasks=[];save();if(code!==0)reject(Error(id+' exited '+code));else resolve(fs.readFileSync(log,'utf8'));});
 });
}
(async()=>{
 state.planSha256=await sha(planPath);save();
 const verifiedSources=[];
 for(const id of new Set(cuts.map(c=>c.sourceVideoId))){
  const file=path.join(sourceDir,id+'.mp4');const expected=new Set(cuts.filter(c=>c.sourceVideoId===id).map(c=>c.sourceSha256));
  if(expected.size!==1||await sha(file)!==[...expected][0])throw Error('Source hash changed: '+id);
  verifiedSources.push({id,path:rel(file),sha256:[...expected][0]});
 }
 state.sources=verifiedSources;save();
 if(measuredV2){
  const previousName=measuredV6?'measured-edit-v5':measuredV5?'measured-edit-v4':measuredV4?'measured-edit-v3':measuredV3?'measured-edit-v2':'measured-edit-v1';
  const previous=read(path.join(__dirname,previousName,'native-review-v1/compiled.json'));
  for(const c of cuts){
   const prior=previous.cuts.find(x=>x.id===c.id&&x.sourceVideoId===c.sourceVideoId&&x.sourceStartFrame===c.sourceStartFrame&&x.sourceEndFrameExclusive===c.sourceEndFrameExclusive&&x.frames===c.frames);
   if(!prior)continue;
   if(await sha(path.join(root,prior.video))!==prior.sha256)throw Error('Retained compiled source changed:'+c.id);
   state.completed.push({...prior,startFrame:c.startFrame,reusedByteIdentical:true,
    originalCompileEvidence:`projects/avoid-game-comparisons/production/${previousName}/native-review-v1/compiled.json`});
  }
  const retained=measuredV6?110:measuredV4?106:measuredV3?107:103;
  if(state.completed.length!==retained)throw Error(`Exactly${retained} unchanged source cuts must be retained.`);
  state.reusedByteIdenticalCuts=retained;state.newSubintervalCuts=measuredV6?1:measuredV5?5:measuredV4?2:measuredV3?1:5;save();
 }
 for(const c of cuts){
  const prior=state.completed.find(x=>x.id===c.id);
  if(prior){if(prior.frames!==c.frames||await sha(path.join(root,prior.video))!==prior.sha256)throw Error('Completed native review changed: '+c.id);continue;}
  const start=c.sourceStartFrame/c.nativeFps,end=c.sourceEndFrameExclusive/c.nativeFps;
  const seek=Math.max(0,Math.floor(start)-1),file=path.join(dest,c.id+'.mp4');
  // Copy original timestamps, then trim the exact native PTS interval. The
  // one-microsecond lower bound accounts for decimal representation only.
  const vf=`trim=start=${Math.max(0,start-.000001).toFixed(9)}:end=${(end-.000001).toFixed(9)},setpts=PTS-STARTPTS,fps=60:round=near,trim=end_frame=${c.frames},setsar=1`;
  const args=['-v','error','-nostdin','-threads','2','-copyts','-ss',String(seek),'-i',path.join(sourceDir,c.sourceVideoId+'.mp4'),
   '-map','0:v:0','-vf',vf,'-frames:v',String(c.frames),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19',
   '-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart',file];
  await run(ff,args,c.id+'-encode');
  const info=JSON.parse(await run(fp,['-v','error','-show_streams','-of','json',file],c.id+'-probe'));
  const v=info.streams.find(s=>s.codec_type==='video');
  if(!v||+v.nb_frames!==c.frames||v.avg_frame_rate!=='60/1'||v.width!==1920||v.height!==1080||info.streams.some(s=>s.codec_type==='audio'))throw Error('Compiled native frame/layout/audio mismatch: '+c.id);
  const decode=await run(ff,['-v','error','-threads','2','-i',file,'-map','0:v:0','-f','null','-'],c.id+'-decode');
  if(decode.trim())throw Error('Whole-cut decode diagnostics: '+c.id);
  state.completed.push({id:c.id,sceneId:c.sceneId,sourceVideoId:c.sourceVideoId,sourceStartFrame:c.sourceStartFrame,
   sourceEndFrameExclusive:c.sourceEndFrameExclusive,nativeFps:c.nativeFps,frames:c.frames,startFrame:c.startFrame,
   video:rel(file),sha256:await sha(file),audioStreams:0,wholeDecodeExitCode:0,wholeDecodeDiagnostics:0,
   composition:{mode:'full-screen-source-review-only',finalFramingApproved:false,
    caution:c.sourceVideoId==='KWDk-csu460'?'These selected intervals are fullscreen final gameplay/VFX, not the earlier inset sinking test. Preserve development context; inspect annotations and every fixed cue.':c.sourceVideoId==='h27ZF-hKKYM'?'Inspect fuel UI in flight excerpts and cup/printed-surface action separately against every fixed cue.':'Inspect action and UI against every final fixed cue.'},
   requiredContextLabel:c.requiredContextLabel||null,finalApproved:false,encodedBoundaryPixelsReviewed:false,allCaptionPixelsApproved:false});
  write(path.join(dest,'compiled.json'),{schemaVersion:1,status:'native-review-only',planSha256:state.planSha256,
   sources:verifiedSources,cuts:state.completed,finalApproved:false});save();console.log(`Native review ${state.completed.length}/${cuts.length}: ${c.id}`);
 }
 state.status='native-review-compiled-all-cues-framing-and-boundaries-pending';state.endedAt=new Date().toISOString();state.exitCode=0;save();
})().catch(e=>{state.status='native-review-compile-failed';state.error=String(e);state.activeTasks=[];state.endedAt=new Date().toISOString();state.exitCode=1;save();console.error(e);process.exitCode=1;});
