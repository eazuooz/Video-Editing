// Current-voice fitting of independent official gameplay excerpts. No media
// is encoded until the exact selection and every caption layout are reviewed.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),{spawnSync}=require('child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n','utf8');};
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;};
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=read(path.join(work,'plan.json')),bank=read(abs('projects/motion-sickness-games/planning/action-map.json'));
const cuts=[],ranges={},meta={};const PWS='PF5L_2g9UVQ',TALOS='6slinvkF0Rs';
const F=t=>Math.round(t*60);
function allocate(s,from,to,specs,focus,paragraphs){
 let cursor=from;
 for(const [id,start,end]of specs){if(cursor>=to)break;
  const frames=Math.min(to-cursor,Math.floor((end-start)*60+1e-4));if(frames<1)continue;
  const file=`shared/assets/game-footage/motion-sickness-games/${id}.mp4`;
  meta[id]??=JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',abs(file)]));
  const video=meta[id].streams.find(s=>s.codec_type==='video');
  if(start+frames/60>Number(video.duration)+.0001)throw Error('Source bounds');
  if(id===TALOS&&((start<42.2&&start+frames/60>42)||(start<74&&start+frames/60>52)))throw Error('Talos title/snow range prohibited');
  if(id===PWS&&[[69,89],[123.5,132],[232,235],[552.5,555],[558,602]].some(([a,b])=>start<b&&start+frames/60>a))throw Error('PWS excluded menu/alert/idle/outro');
  const used=ranges[id]??=[];if(used.some(([a,b])=>start<b-.0001&&start+frames/60>a+.0001))throw Error('Repeated source interval');used.push([start,start+frames/60]);ranges[id]=used;
  const c={id:String(cuts.length+1).padStart(3,'0'),scene:s.id,sourceId:id,file,sourceIn:start,sourceOut:start+frames/60,
   reviewedSourceEnd:end,frames,seconds:frames/60,localStartFrame:cursor,localEndFrame:cursor+frames,
   timelineStart:s.start+cursor/60,timelineEnd:s.start+(cursor+frames)/60,crop:null,
   sourceLabel:id===PWS?'PowerWash Simulator · FuturLab 개발 시연 (2022 WIP)':'The Talos Principle 2 · 공식 플레이 (2023)',
   visibleAction:focus,viewerFocus:focus,paragraphs,diagramConnection:bank.chapters.find(v=>v.scene===s.id).diagramConnection,
   classification:'actual-existing-game-action',speed:1,loop:false,captionCenter:[960,970],
   continuity:'Independent excerpts; no uninterrupted or controlled comparison claimed.',sourceAudio:'excluded; approved continuous Nimbus',
   nativeBoundaryAndCaptionReview:'pending'};
  s.cuts.push(c);cuts.push(c);cursor+=frames;
 }
 if(cursor!==to)throw Error(`Scene${s.id} short by${(to-cursor)/60}s; inspect fresh action, never repeat/slow/idle.`);
}
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 s.cuts=[];
 if(s.id==='01'){
  allocate(s,0,F(9.983333),[[PWS,48,57.983334]],'Floor/nozzle sweep rotates the background playground at normal speed.',[1]);
  allocate(s,F(9.983333),F(34.166667),[[PWS,90.5,98.9],[PWS,99,114.783334]],'Tool aim moves independently against playground posts/floor; do not infer spraying in the first independent-aim excerpt.',[2,3,4]);
  allocate(s,F(34.166667),s.frames,[[PWS,169,188.433334]],'Actual roundabout washing continues under WIP/no-experiment disclaimer and camera-responsibility question; observe spray target vs background.',[5,6]);
 }else if(s.id==='03'){
  allocate(s,0,F(19.016667),[[PWS,132,151.016667]],'Independent floor aim leaves background stairs and trees locally stable.',[1,2]);
  allocate(s,F(19.016667),F(27.45),[[PWS,156.5,164.933334]],'Aim reaches the view edge; roundabout enters when the view turns.',[3]);
  allocate(s,F(27.45),F(38.4),[[PWS,189,199.95]],'Nozzle spray tracks the roundabout surface while the background is locally steady.',[4]);
  allocate(s,F(38.4),s.frames,[[PWS,199.95,224.116667]],'Further roundabout/floor target work and view changes preserve looking around; continued normal-speed work supports the final observation.',[5,6]);
 }else if(s.id==='05'){
  allocate(s,0,F(8.883333),[[PWS,268,276.883334]],'Player moves among nearby posts; nearby geometry and distant trees shift.',[1]);
  allocate(s,F(8.883333),F(17.716667),[[PWS,301,309.833334]],'Repositioning reveals another surface rather than removing needed motion.',[2]);
  allocate(s,F(17.716667),F(26.983333),[[PWS,310,319.266667]],'View looks upward and nozzle washes high boards/structure.',[3]);
  allocate(s,F(26.983333),s.frames,[[PWS,339.1,367.066667],[PWS,319.266667,326.766667]],'Other surface: settle position then sweep spray across posts/broad faces. Final independent upper-face excerpt observes task still continuing, under explicit separate-cut disclaimer.',[4,5,6]);
 }else if(s.id==='07'){
  allocate(s,0,F(8.566667),[[TALOS,31.033333,35.666667],[TALOS,36,39.933333]],'Separate platform/device puzzle actions: travel, look up toward the device.',[1]);
  allocate(s,F(8.566667),F(14.766667),[[TALOS,47.8,52],[TALOS,40,42]],'Different puzzle views rotate walls and lasers; title/snow footage excluded.',[2]);
  allocate(s,F(14.766667),F(26.5),[[TALOS,16,20.733333],[TALOS,23.033333,30.033333]],'Independent puzzle direction/action changes under explicit separate-cut/orientation question.',[3]);
  allocate(s,F(26.5),F(30.933333),[[PWS,251.5,255.933334]],'Look up from beneath the monkey bars while spray tracks an overhead face.',[4]);
  allocate(s,F(30.933333),F(33.933333),[[PWS,265,268]],'The view turns back toward the wooden structure: posts and boards become visible as the narrated other face is introduced.',[4]);
  allocate(s,F(33.933333),F(37.366667),[[PWS,289,292.433334]],'A separate near-post wash excerpt visibly contains both boards and posts under the direction/landmark sentence.',[4]);
  allocate(s,F(37.366667),s.frames,[[PWS,367.066667,392.85]],'View/target changes around the structure, then a turn/move toward the boundary fence. Observe heading and retained environmental landmarks under the last instruction; do not describe the final fence movement as washing.',[5,6]);
 }else if(s.id==='09'){
  allocate(s,0,F(20.533333),[[PWS,408,428.533334]],'Slide washing, new viewpoint and spray-target relation.',[1,2]);
  allocate(s,F(20.533333),F(29.333333),[[PWS,465,473.8]],'Nearby boards/posts remain visible with nozzle and the worked face.',[3]);
  allocate(s,F(29.333333),F(39.933333),[[PWS,326.766667,337.366667]],'Independent upper-board/post cleaning preserves aim-target relationship under the implementation caveat.',[4]);
  allocate(s,F(39.933333),s.frames,[[PWS,437,461.8]],'Further slide/structure work: observe view, tool, surface and reacquiring another target. Actual task continues, no body-state result claimed.',[5,6]);
 }else if(s.id==='11'){
  allocate(s,0,F(8.966667),[[PWS,484.4,493.366667]],'Nearby other-face wash: nozzle/spray destination visible.',[1]);
  allocate(s,F(8.966667),F(19.25),[[PWS,510,520.283334]],'Turning/repositioning around posts and boards reveals the next worked face.',[2]);
  allocate(s,F(19.25),F(27.833333),[[PWS,528,536.583334]],'View looks up toward crossbars; whole-view and target-relative tool movement can be compared.',[3]);
  allocate(s,F(27.833333),F(49.083333),[[PWS,536.583333,552.4],[PWS,521,526.433334]],'Further target sweeps and view changes, with no all-comfort claim; label necessary motion and tool changes under the audit instruction.',[4,5]);
  allocate(s,F(49.083333),s.frames,[[PWS,493.366667,504.433334],[PWS,429,435]],'Independent worked-face and slide washing continue under the final question about recognizing the same goal through other controls.',[6]);
 }
 if(s.cuts.reduce((n,c)=>n+c.frames,0)!==s.frames)throw Error('Coverage mismatch');
}
plan.cuts=cuts;plan.sourceRangeAudit={noRepeatedInterval:true,ranges};plan.finalSourceTimingApproved=false;
write(path.join(work,'plan.json'),plan);write(path.join(work,'cut-selection.json'),{status:'measured-selected-awaiting-direct-native-and-caption-review',existingGamesOnly:true,normalClock:true,cuts});
if(process.argv.includes('--plan-only')){console.log(JSON.stringify({cuts:cuts.length,plannedSeconds:cuts.reduce((n,c)=>n+c.frames,0)/60,approval:false}));process.exit(0);}
const gate=read(path.join(work,'final-source-cut-review.json'));
if(!gate.approved||gate.selectionSha256!==sha(path.join(work,'cut-selection.json')))throw Error('Exact native action/caption review gate required.');
for(const c of cuts)c.nativeBoundaryAndCaptionReview='direct-reviewed; encoded/final pixels still pending';
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
for(const s of plan.scenes.filter(s=>s.classification==='actual')){
 const files=[];
 for(const c of s.cuts){
  const dest=path.join(work,`cut-${c.id}.mp4`),label=path.join(work,`source-label-${c.id}.txt`);write(label,c.sourceLabel+' · 발췌');
  const textfile=rel(label).replaceAll(':','\\:');
  const vf=`fps=60,scale=1920:1080,setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${textfile}':fontsize=25:fontcolor=0x073c32:x=(w-tw)/2:y=30:box=1:boxcolor=white@0.9:boxborderw=10`;
  run('ffmpeg',['-v','error','-y','-threads','2','-ss',String(c.sourceIn),'-i',abs(c.file),'-frames:v',String(c.frames),'-vf',vf,...enc,dest]);c.video=rel(dest);files.push(dest);
 }
 const list=path.join(work,`scene-${s.id}-concat.txt`);write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
 const dest=abs(`shared/output/motion-sickness-games/actual-scenes/scene${s.id}.mp4`);fs.mkdirSync(path.dirname(dest),{recursive:true});
 run('ffmpeg',['-v','error','-y','-f','concat','-safe','0','-i',list,'-c','copy',dest]);
 const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-of','json',dest]));
 if(probe.streams.some(v=>v.codec_type==='audio')||Number(probe.streams[0].nb_frames)!==s.frames)throw Error('Compiled duration/audio mismatch');
 s.actualVideo=rel(dest);s.actualMediaVerified={...probe.streams[0],sha256:sha(dest)};
}
plan.finalSourceTimingApproved=true;plan.actualFootageMeasuredAndApproved=true;
write(path.join(work,'plan.json'),plan);console.log('Six audio-free actual chapter MP4s compiled; final visual QA and MC installation still required.');
