const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='production/research/game-lighting-history',project='projects/game-lighting-history-03';
const read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8'));
const sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const write=(x,v)=>fs.writeFileSync(path.join(root,x),JSON.stringify(v,null,2)+'\n');
const input=base+'/local/native-action-support-v13-ddgi-additional/execution.json',a=read(input);
const out=project+'/production/native-ddgi-additional-direct-review-v13.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve completed direct review');
if(a.status!=='action-sequences-ready')throw Error('Completed extraction required');
const notes=[
 '124–125 lit boxes/Edit menu;126 menu;127–132 plugin-manager search. Installation controls, not an illumination result.',
 '133–137 plugin list and hover;138 reframes boxes;139–141 hold. Exclude installation and prolonged unchanged views.',
 '142–148 unchanged boxes;149–150 Outliner selection. No new lighting comparison.',
 '151 hover,152 selects postprocess actor,153–156 details scroll with unchanged lighting. Do not count a menu hold as an illumination process.',
 '193–201 actor-creation menus over unchanged dark boxes. Exclude prolonged menus.',
 '202 still actor menu;203 closes menu;204 new selected volume bounds and properties. Boundary/setup context only.',
 '318–321 camera around the blue-lit box with probe visualization;322–326 ContentBrowser view/menu holds. The spheres visualize probes rather than additional lamps.',
 '327–329 ContentBrowser/save dialog;330 opens city map;331 volume selection;332–334 nearly unchanged;335 probe visualization appears. Do not infer measured performance from counters.',
 '336–341 active city/probe camera;342 close source annotation;343–344 nearly unchanged close annotation. The64×64×4=16384 count belongs to this demonstration.',
 '345–353 prolonged unchanged city/probe/annotation view. Exclude.',
 '354–362 same unchanged city/probe/annotation view. Exclude.'
];
let i=0;const reviewed=a.completed.map(r=>({...r,boards:r.boards.map(b=>{
 if(sha(b.path)!==b.sha256)throw Error('Changed board '+b.path);
 for(const s of b.samples)if(sha(s.path)!==s.sha256)throw Error('Changed sample '+s.path);
 return {...b,directlyViewed:true,note:notes[i++]};
})}));
if(i!==notes.length)throw Error('Direct board count mismatch');
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),input:{path:input,sha256:sha(input)},reviewed,
 boardCount:i,temporalSampleCount:90,allBoardsDirectlyViewed:true,allTemporalSamplesDirectlyViewed:true,
 candidateActionRanges:[{source:'rtxgi-ue5-preview2-2022',ranges:[[318,322],[335,342]]}],
 method:'All11 temporal boards/90 samples directly read; setup, long static holds and source-specific counts separated from actual camera/control actions.',
 continuousFullMotionReviewed:false,finalUseApproved:false,allFinalCaptionPixelsReviewed:false,rightsApproved:false,sourceAudioUsed:false,newGitRasterCount:0,localOnly:true};
write(out,record);
const cp=base+'/checkpoint.json',c=read(cp),lease=read('shared/output/GPU_HANDOFF.json'),session=read(project+'/production/native-guides-tts-session-v1.json');
if(lease.token!=='54794caf-f8bf-4b7d-8d28-b6dc90ff93d1'||lease.state!=='waiting_for_current_job_boundary')throw Error('Handoff changed; read real execution first');
c.updatedAt=new Date().toISOString();
c.episode03NativeAdditionalReview={path:out,sha256:sha(out),boards:11,temporalSamples:90,allBoardsDirectlyViewed:true,continuousFullMotionReviewed:false,finalUseApproved:false};
c.ownedJobsRunning=[{pid:lease.coordinator.pid,createTime:lease.coordinator.createTime,commandLine:lease.coordinator.command,sessionId:session.sessionId,stage:lease.state,leaseToken:lease.token,cpuThreads:2,gpuJobs:0,ttsModelLoaded:false,completedGuides:0,totalGuides:20,session:project+'/production/native-guides-tts-session-v1.json',next:'Let current research run seal checkpoint/validation/done; coordinator alone grants TTS and restores original queue.'}];
c.ownedActiveWork=c.ownedJobsRunning;
write(cp,c);
console.log(JSON.stringify({review:out,boards:i,samples:90,guideTtsModelLoaded:false,waitingCoordinatorPid:lease.coordinator.pid,sessionId:session.sessionId,newRasterOrMediaStaged:false}));
