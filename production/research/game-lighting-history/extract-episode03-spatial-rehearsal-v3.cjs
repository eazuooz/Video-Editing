// Immutable narrated rehearsal QA. All media/images are local-only; no final-video approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),rel='production/research/game-lighting-history/local/episode03-spatial-rehearsal-v3',dir=path.join(root,rel),qa=path.join(dir,'qa');
const read=p=>JSON.parse(fs.readFileSync(path.resolve(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const planPath=rel+'/plan.json',plan=read(planPath),frameMap=new Map();
function addFrame(frame,reason){frame=Math.min(plan.frames-1,Math.max(0,frame));const f=frameMap.get(frame)||{frame,reasons:[]};f.reasons.push(reason);frameMap.set(frame,f);}
function addTime(seconds,reason){addFrame(Math.round(seconds*60),reason);}
for(const c of plan.chapters){
 for(const cue of c.cues){
  addTime(c.timelineFrom+(cue.from+cue.to)/2,`${c.scene}:cue${cue.id}:center`);
  const first=Math.ceil((c.timelineFrom+cue.from)*60-1e-7),off=Math.ceil((c.timelineFrom+cue.to)*60-1e-7);
  for(const [f,k]of [[first-1,'before-onset'],[first,'onset'],[off-1,'last-on'],[off,'first-off']])addFrame(f,`${c.scene}:cue${cue.id}:${k}`);
 }
 for(const p of c.paragraphs)for(const [k,t]of Object.entries({before:Math.max(p.from,p.move[0]-.15),middle:(p.move[0]+p.move[1])/2,after:Math.min(p.to-.05,p.move[1]+.15)}))addTime(c.timelineFrom+t,`${c.scene}:paragraph${p.index+1}:${k}`);
 for(const [f,k]of [[Math.round(c.timelineFrom*60)-1,'before-chapter'],[Math.round(c.timelineFrom*60),'chapter-onset']])addFrame(f,`${c.scene}:${k}`);
}
const frames=[...frameMap.values()].sort((a,b)=>a.frame-b.frame),planOnly=process.argv.includes('--plan-only');
const snapshotNames=['narrated-runtime-v3.tsx','narrated-data-v3.json','narrated-project-v3.ts',...plan.chapters.flatMap(c=>[`narrated-${c.scene}-v3.tsx`,`narrated-${c.scene}-v3.meta`])];
const inputs=[{path:planPath,sha256:sha(path.join(root,planPath))},...plan.inputs,...snapshotNames.map(n=>{const p='motion-canvas/src/projects/game-lighting-history-03/spatial/'+n;return{path:p,sha256:sha(path.join(root,p))};})];
const extractionPlan={createdAt:new Date().toISOString(),scope:'All257cue centers and every on/off boundary plus84before/middle/after narration-timed motion poses and14chapter boundaries. Rehearsal only, not gameplay allocation, final mix, final episode or human listening approval.',chapters:14,paragraphs:84,cues:257,frames,inputs,plannedFrames:plan.frames,actualImagesExtracted:0,allPixelsReviewed:false,finalVideoApproved:false,localOnly:true};
const qp=path.join(dir,'qa-plan-v3.json');
if(planOnly){if(fs.existsSync(qp))throw Error('Existing extraction plan preserved');fs.writeFileSync(qp,JSON.stringify(extractionPlan,null,2)+'\n');console.log(JSON.stringify({plan:path.relative(root,qp),uniqueFrames:frames.length,boards:Math.ceil(frames.length/6),actualImagesExtracted:0}));process.exit(0);}
const frozen=read(qp);for(const i of frozen.inputs)if(sha(path.join(root,i.path))!==i.sha256)throw Error('Frozen rehearsal input changed:'+i.path);
const execution=read('production/research/game-lighting-history/local/current-render-execution-v1.json');
if(execution.status!=='complete'||execution.exitCode!==0||!execution.command.includes('narrated-project-v3.mp4'))throw Error('This rehearsal exporter has not actually completed');
if(fs.existsSync(path.join(qa,'extraction.json')))throw Error('Existing complete QA preserved');
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe',statePath=path.join(dir,'qa-execution-v3.json'),startedAt=new Date().toISOString();
function state(s){fs.writeFileSync(statePath,JSON.stringify({startedAt,ownerPid:process.pid,command:process.argv,cpuThreads:2,gpuJobs:0,finalVideo:false,...s},null,2)+'\n');}
function run(exe,args,step){state({status:'running',step,childCommand:[exe,...args]});const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:32*1024*1024});if(r.status!==0)throw Error(step+':'+r.stderr);return{command:[exe,...args],exitCode:r.status,stdout:r.stdout,stderr:r.stderr};}
try{
 const source=path.join(root,'production/research/game-lighting-history/local/black-proof-v3/narrated-project-v3.mp4'),video=path.join(dir,'all14-chapters.captioned.mp4');
 if(fs.existsSync(video))throw Error('Existing rehearsal copy preserved');fs.copyFileSync(source,video);fs.mkdirSync(qa,{recursive:true});
 const probeRun=run(ffprobe,['-v','error','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,duration,nb_frames,nb_read_frames,sample_rate,channels','-show_entries','format=duration','-of','json',video],'whole-frame-probe'),probe=JSON.parse(probeRun.stdout),v=probe.streams.find(s=>s.codec_type==='video'),a=probe.streams.find(s=>s.codec_type==='audio');
 if(v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||v.time_base!=='1/90000'||!a||Number(v.nb_read_frames)<plan.frames)throw Error('Incomplete or unexpected rehearsal');
 const decode=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-f','null','NUL'],'whole-decode');
 const extraction=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-vf',`select='${frozen.frames.map(f=>`eq(n,${f.frame})`).join('+')}'`,'-vsync','0','-threads','2',path.join(qa,'frame-%04d.png')],'all-planned-frames');
 const extracted=frozen.frames.map((f,i)=>({...f,path:`${rel}/qa/frame-${String(i+1).padStart(4,'0')}.png`,sha256:sha(path.join(qa,`frame-${String(i+1).padStart(4,'0')}.png`))}));
 const boards=[];for(let i=0;i<Math.ceil(extracted.length/6);i++){const n=Math.min(6,extracted.length-i*6),out=path.join(qa,`board-${String(i+1).padStart(3,'0')}.png`);run(ffmpeg,['-hide_banner','-v','error','-threads','2','-start_number',String(i*6+1),'-i',path.join(qa,'frame-%04d.png'),'-vf',`scale=960:540,tile=2x3:nb_frames=${n}`,'-frames:v','1','-threads','2',out],'board-'+(i+1));boards.push({path:path.relative(root,out).replaceAll('\\','/'),sha256:sha(out),directlyViewed:false,frameIndices:[i*6+1,i*6+n]});}
 const record={createdAt:new Date().toISOString(),scope:frozen.scope,video:{path:`${rel}/all14-chapters.captioned.mp4`,sha256:sha(video),probe},exporter:execution,inputs:frozen.inputs,qaPlanSha256:sha(qp),plannedFrames:plan.frames,observedFrames:Number(v.nb_read_frames),endpointDifference:Number(v.nb_read_frames)-plan.frames,wholeDecode:decode,probeCommand:probeRun.command,extractionCommand:extraction.command,frames:extracted,boards,allCueCentersReviewed:false,allCaptionBoundaryPixelsReviewed:false,allRehearsalPixelsReviewed:false,fullEpisodeApproved:false,finalMix:false,localOnly:true};
 fs.writeFileSync(path.join(qa,'extraction.json'),JSON.stringify(record,null,2)+'\n');state({status:'complete-awaiting-direct-review',exitCode:0,endedAt:new Date().toISOString(),frames:extracted.length,boards:boards.length});console.log(JSON.stringify({frames:extracted.length,boards:boards.length,observedFrames:record.observedFrames,wholeDecode:0}));
}catch(e){state({status:'failed-preserving-render-and-extracted-files',error:String(e),endedAt:new Date().toISOString()});throw e;}
