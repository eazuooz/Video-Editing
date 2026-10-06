const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..'),base=path.relative(root,__dirname).replaceAll('\\','/'),now=new Date().toISOString();
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function write(p,d){const f=path.join(root,p),t=f+'.'+process.pid+'.tmp';fs.writeFileSync(t,JSON.stringify(d,null,2)+'\n');for(let i=0;;i++){try{fs.renameSync(t,f);return;}catch(e){if(i===19||!['EPERM','EACCES','EBUSY'].includes(e.code))throw e;await sleep(150);}}}
const notes=[
 'Room firing and ceiling target; clean action edges.',
 'Sewer-platform firing ends with a weapon throw.',
 'Alley kick/firing reaches stair/catwalk targets; montage transitions, not a single causal encounter.',
 'Catwalk kick ends with a purple target close to the camera.',
 'Room target/flying weapon then ceiling gunfire.',
 'Corridor crossbow/kick ends at a bathroom target; do not call the entire interval rooftop gameplay.',
 'Bathroom kick to pizza-shop kick; source montage boundary retained.',
 'Disco shooting to downward flamethrower action.',
 'Sewer furniture movement and plunger kick.',
 'Sewer movement/firing to red-room kick.',
 'REJECT: last included frames show a Gunbrella acquisition toast and stationary bridge character. The earlier coarse candidate did not justify the full interval.',
 'Character movement and umbrella opening end amid projectiles/upward aim.',
 'Airborne umbrella/rope/enemy action ends at ground horizontal projectile block; no perfect-guard or immunity claim.',
 'Ground fire ends with an umbrella rise beside the vertical column.',
 'Run to upward aim/ceiling-turret projectile.',
 'Junkyard jump/umbrella with approaching projectiles; distinct path from the other showcase.',
 'Water-surface action to room/eye arena, not one continuous water/library encounter.',
 'Eye-arena jump and side firing.',
 'Large beast and umbrella leap above yellow projectiles.',
 'Movement beneath ceiling turret to rising umbrella/attack.',
 'Run through the crusher passage.',
 'Run between twin launchers to rising umbrella and arcing projectiles.',
 'Distinct junkyard traversal/wall jump/shot sequence.',
 'Mechanical-arm turret traversal/jump ends at gunfire.',
 'Suspended-platform descent with separated left/right firing.',
 'Barrel traversal and upper-stair enemy firing.',
 'Zipline/hook firing to wall-side upward aim.',
 'Wall jump to airborne upper-room firing.',
 'Inverted hang with independently directed guns versus floor targets.',
 'Vertical swing/aim amid pipes and electricity.',
 'Window/fall/room-entry firing against floor and airborne enemies.',
 'Train-boss arena movement/firing; preserve top health UI. No victory or quantified damage claim.',
 'Two-level simultaneous combat, gunfire and kicks.',
 'RESERVE, excluded from the selected plan: skateboard/grapple action has internal trailer framing/letterbox; final full-screen crop is not approved. These edges do not establish an advertising overlay.',
 'First bathroom split aim and drop through the second bathroom.',
 'Second bathroom/floor transition ends above a grate.',
 'Grate jump to lower corridor spinning fire.',
 'Corridor jump to lower room and upper-target aim.',
 'Wall/shaft climb ends crouched on a platform; descending lift after the out-point excluded.'
];
(async()=>{
 const edges=read(base+'/cut-edges-execution-v1.json'),bank=read(base+'/source-action-bank-v1.json');
 if(edges.boards.length!==39||edges.frameSlots!==234||bank.clips.length!==39)throw Error('Unexpected review inputs');
 for(const [i,b] of edges.boards.entries()){if(b.actionId!==bank.clips[i].id||hash(b.board)!==b.sha256)throw Error('Changed board');for(const t of b.tiles)if(hash(t.path)!==t.sha256)throw Error('Changed edge pixel');b.directlyRead=true;b.reviewedAt=now;b.observation=notes[i];b.selectedSourceEdgeApproval=![10,33].includes(i);}
 edges.allDirectlyRead=true;edges.reviewedAt=now;edges.status='all39-cut-edge-boards-directly-read';edges.finishedAt=now;edges.finalPixelApproval=false;await write(base+'/cut-edges-execution-v1.json',edges);
 const selected=bank.clips.filter(c=>!['action-11','action-34'].includes(c.id)).map(c=>({...c,exactEdgeApproval:true,sourceEdgeReviewedAt:now,edgeObservation:notes[Number(c.id.slice(-2))-1],edgeBoard:edges.boards.find(b=>b.actionId===c.id).board,finalCutAndCaptionApproval:false}));
 for(const c of selected){if(c.id==='action-06')c.visibleAction='Corridor crossbow/kick to bathroom target';if(c.id==='action-17')c.visibleAction='Water-surface action, room transition and eye-arena combat';}
 const excluded=bank.clips.filter(c=>!selected.some(s=>s.id===c.id)).map(c=>({...c,decision:c.id==='action-11'?'rejected-acquisition-toast':'reserved-unapproved-internal-framing',reason:notes[Number(c.id.slice(-2))-1],countsTowardSelectedActualSeconds:false}));
 const next={...bank,schemaVersion:2,createdAt:now,status:'37-selected-source-intervals-edge-reviewed; final framing/captions/timing pending',previousCandidateBank:base+'/source-action-bank-v1.json',clipCount:selected.length,candidateSeconds:selected.reduce((n,c)=>n+c.seconds,0),clips:selected,excluded,allEdgesDirectlyRead:true,ratioApproved:false,finalCutAndCaptionApproval:false,imagesGitPolicy:'local-only'};
 await write(base+'/source-action-bank-v2.json',next);
 await write(base+'/cut-edge-direct-review-v1.json',{schemaVersion:1,slug:'familiar-game-rules',reviewedAt:now,boardCount:39,frameSlots:234,all39BoardsDirectlyRead:true,selectedClipCount:selected.length,selectedSourceSeconds:next.candidateSeconds,excluded,edgeManifest:base+'/cut-edges-execution-v1.json',edgeManifestSha256:hash(base+'/cut-edges-execution-v1.json'),sourceBank:base+'/source-action-bank-v2.json',sourceBankSha256:hash(base+'/source-action-bank-v2.json'),sourceAudioUsed:false,currentBindingsOrDeviceSupportProven:false,finalCaptionPixelsApproved:false,finalRatioApproved:false,resumeExitCodeObserved:0,priorQueueWriteFailurePreserved:base+'/cut-edges-execution-v1.initial-failure.json',priorSecondSourceExitCodeObserved:false,imagesGitPolicy:'local-only'});
 const sess=read(base+'/cut-edges-execution-v1.resume-session.json');Object.assign(sess,{observedAt:now,status:'finished-exit0-all39-edge-boards-directly-read',exitCode:0,alive:false,worker:null});await write(base+'/cut-edges-execution-v1.resume-session.json',sess);
 const g=read('projects/familiar-game-rules/sources/game-candidates.json');Object.assign(g,{updatedAt:now,stage:'selected-source-edges-approved-independent-script-pending',sourceBank:base+'/source-action-bank-v2.json',sourceEdgeReview:base+'/cut-edge-direct-review-v1.json',selectedSourceIntervals:37,selectedSourceSeconds:next.candidateSeconds,all39EdgeBoardsDirectlyRead:true,selectedSourceEdgesApproved:true,actualCutApproval:false,finalCaptionPixelsApproved:false});await write('projects/familiar-game-rules/sources/game-candidates.json',g);
 const q=read('production/batches/sakurai-planning-game-design/queue.json'),item=q.items.find(x=>x.slug==='familiar-game-rules');Object.assign(item,{updatedAt:now,stage:g.stage,nextAction:'Create independent KO/EN overview, complete script and per-script Motion Canvas scenes using reviewed actions. Preserve useful explanation; acquire additional unique official action if measured narration needs more than135.394833s. No loop/slowdown/quota filler.',execution:{...item.execution,status:'edge resume finished exit0; all39boards234slots read',pid:null,sessionId:null,alive:false,activeTasks:[],lastObservedAt:now,lastCompletedPid:41024,lastCompletedSessionId:49678,lastExitCode:0},sourceReview:{...item.sourceReview,edgeBoards:39,edgeFrameSlots:234,allEdgeBoardsDirectlyRead:true,selectedIntervals:37,selectedSourceSeconds:next.candidateSeconds,selectedSourceEdgesApproved:true,finalCaptionPixelsApproved:false}});q.updatedAt=now;q.lastProgressAt=now;await write('production/batches/sakurai-planning-game-design/queue.json',q);
 for(const p of ['projects/familiar-game-rules/production/latest-checkpoint.json',base+'/latest-checkpoint.json']){const x=read(p);Object.assign(x,{updatedAt:now,stage:item.stage,execution:item.execution,nextAction:item.nextAction,sourceReview:item.sourceReview,newScriptCreated:false,newTtsStarted:false});await write(p,x);}
 console.log(JSON.stringify({boards:39,frameSlots:234,selectedIntervals:37,selectedSeconds:next.candidateSeconds,renderOrFinalPixelsApproved:false}));
})();
