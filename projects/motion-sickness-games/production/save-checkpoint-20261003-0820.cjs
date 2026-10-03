// Save observed work only. The live repair runner remains authoritative.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/motion-sickness-games/production/';
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p, o) => fs.writeFileSync(path.join(root, p), JSON.stringify(o, null, 2) + '\n');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const at = new Date().toISOString();
const processes = spawnSync('powershell', ['-NoProfile', '-Command', 'Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(47052,58552,7540,39360,43444,39724,35852) } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress'], {encoding:'utf8', windowsHide:true});
if (processes.status !== 0) throw Error(processes.stderr);
const raw = processes.stdout.trim() ? JSON.parse(processes.stdout) : [];
const rows = Array.isArray(raw) ? raw : [raw];
const isAlive = pid => rows.some(r => r.ProcessId === pid);
const initial = read(base + 'resource-runner.json');
const repair = read(base + 'repair-phrases1.json');
if (initial.status !== 'tts-asr-ready-for-direct-review' || isAlive(7540)) throw Error('Initial pipeline observation changed; review before saving.');
if (!isAlive(47052) || repair.status === 'failed') throw Error('Repair runner requires a fresh audit.');
const source = 'motion-canvas/src/projects/motion-sickness-games/scenes/camera-concepts.tsx';
const v1 = read(base + 'lookdev-v1/inspection.json');
Object.assign(v1, {directVisualReview:'rejected-layout-overlaps', reviewedAt:at, reviewedImageCount:18,
  findings:['02 body glyphs overlapped detail text.', '04 crosshair/arrow overlapped title/detail.', '06 proposal text overlapped control rows.', '08 landmarks rotated about the wrong origin and left their panels.', '12 coaching footer crowded card shadows.'],
  supersededBy:base+'lookdev-v2/inspection.json', finalNarratedVideo:false});
write(base+'lookdev-v1/inspection.json', v1);
const v2 = read(base + 'lookdev-v2/inspection.json');
Object.assign(v2, {directVisualReview:'passed-silent-explanation-composition', reviewedAt:at, reviewedImageCount:18,
  sourceCode:{path:source, sha256:sha(source)},
  fixes:['Separated body illustration and detail text.', 'Separated crosshair/arrow and card labels.', 'Separated option title, detail and controls.', 'Centered each rotating landmark group in its own panel.', 'Separated coaching footer and lower card shadows.'],
  notes:'All six explanation scenes were read at early/middle/late samples. White 2.5D depth, comparisons, arrows and labels are legible after fixes. No final narration timing or burned subtitle cue has been reviewed in this silent lookdev.',
  technicalChecks:{probe:{command:'ffprobe -v error -show_entries stream=codec_type,width,height,r_frame_rate,nb_frames:format=duration -of json shared/output/motion-canvas/motion-sickness-games-lookdev-v2.mp4',exitCode:0,width:1920,height:1080,fps:60,frames:2880,seconds:48,audioStreams:0},
    fullDecode:{command:'ffmpeg -v error -i shared/output/motion-canvas/motion-sickness-games-lookdev-v2.mp4 -f null NUL',exitCode:0,errorOutput:''}},
  narrationTimingReview:'pending', everyCaptionReview:'pending', bodyRatioApproved:false, finalNarratedVideo:false});
write(base+'lookdev-v2/inspection.json',v2);
const scenes=read(base+'scene-authoring.json');
const typecheck=spawnSync(process.execPath,['node_modules/typescript/bin/tsc','-p','tsconfig.motion-sickness-games.json'],{cwd:path.join(root,'motion-canvas'),encoding:'utf8',windowsHide:true});
if(typecheck.status!==0)throw Error(typecheck.stdout+typecheck.stderr);
Object.assign(scenes,{updatedAt:at,lookdev:{revision:'v2',silent:true,seconds:48,frames:2880,review:base+'lookdev-v2/inspection.json',directlyReviewedImages:18,compositionPassed:true,finalNarrationTimingInstalled:false,finalCaptionReview:false},
  typecheck:{at:new Date().toISOString(),command:'bundled Node node_modules/typescript/bin/tsc -p tsconfig.motion-sickness-games.json (motion-canvas cwd)',exitCode:typecheck.status,scope:'layout fix source; silent composition only; final timing/captions pending'}});
write(base+'scene-authoring.json',scenes);
const initialSession=read(base+'runner-session.json');
Object.assign(initialSession,{observedAt:at,runnerAlive:false,statusAtObservation:initial.status,currentChildren:initial.children,finishedAt:initial.finishedAt,doNotRestart:true,contentReview:base+'voice-approval-initial.json',supersededActiveRunner:base+'repair-phrases1.json'});
write(base+'runner-session.json',initialSession);
const repairSession={recordedAt:at,toolSessionId:8552,pid:47052,runnerAlive:true,statusAtObservation:repair.status,state:base+'repair-phrases1.json',runner:base+'repair-phrases1.cjs',currentChildren:repair.children,inputsLocked:true,doNotDuplicate:true,automaticallyApproved:false,humanListening:'pending'};
write(base+'repair1/runner-session.json',repairSession);
const checkpointPath=base+'checkpoint-20261003-0820.json';
const checkpoint={recordedAt:at,slug:'motion-sickness-games',initialPipeline:{toolSessionId:54795,pid:7540,alive:false,status:initial.status,finishedAt:initial.finishedAt,children:initial.children,doNotRestart:true},
  initialDirectReview:base+'voice-approval-initial.json',allInitialScenesRead:12,allInitialParagraphsRead:60,acceptedInitialScenes:['01','02','08','09','11','12'],
  targetedRepair:{...repairSession,candidateParagraphs:7,affectedScenes:['03','04','05','06','07','10'],request:base+'repair1/request.json',sourcePCMUnchangedUntilCandidateAcceptance:true,unchangedScriptParagraphs:53,allSixExplanationClaimsPreserved:true},
  compose:{script:base+'compose-repaired-v2.py',status:'syntax-checked-not-run',gate:'All seven current-hash candidate ASR paragraphs must be directly accepted first; preserve unaffected v1 PCM in a separate v2, then review full current-hash12-scene ASR including every splice and ending.'},
  lookdev:scenes.lookdev,vite:{port:9214,pid:58552,toolSessionId:40370,alive:isAlive(58552),reuseWhenAlive:true},observedProcesses:rows,
  measuredSourceCutsApproved:false,bodyRatioApproved:false,finalMix:false,finalRender:false,collected:false,privateUploaded:false,gitDelivered:false,humanListening:'pending',
  nextAction:'Reuse repair47052/session8552. Directly review seven candidate paragraphs when ready. Do not rerun ended initial54795/39360/43444, contextualASR51332 or silent lookdev43345/10406. No full narration/cut/mix/ratio/private delivery approval yet.'};
write(checkpointPath,checkpoint);
const queuePath='production/batches/sakurai-planning-game-design/queue.json';
const q=read(queuePath),item=q.items.find(i=>i.slug==='motion-sickness-games');
if(item.status!=='in-progress')throw Error('Queue item changed; stop.');
const e=item.execution;
e.initialPipeline={sessionId:54795,pid:7540,runner:base+'resource-runner.cjs',state:base+'resource-runner.json',status:initial.status,finishedAt:initial.finishedAt,alive:false,children:initial.children,contentReview:base+'voice-approval-initial.json',doNotRestart:true};
Object.assign(e,{sessionId:8552,toolSessionId:8552,pid:47052,workerPid:null,phase:'initial-ASR-reviewed-targeted-repair',status:repair.status,startedAt:repair.startedAt,updatedAt:at,runner:base+'repair-phrases1.cjs',state:base+'repair-phrases1.json',log:repair.runnerLog,logs:{runner:repair.runnerLog,candidates:repair.candidateLog},children:repair.children,sessionRecord:base+'repair1/runner-session.json',resourceToolSessionId:54795,actualSessionObservedAt:at,latestCheckpoint:checkpointPath,
  repair1:{...e.repair1,...repair,toolSessionId:8552,alive:true,runner:base+'repair-phrases1.cjs',state:base+'repair-phrases1.json'},
  sceneCode:{...e.sceneCode,lookdevRendered:true,lookdevRevision:'v2',silentLookdevVisualApproval:true,lookdevEvidence:base+'lookdev-v2/inspection.json',visualApproval:false,measuredTimingInstalled:false},
  vite:checkpoint.vite,activeTasks:repair.children.filter(c=>c.status==='running')});
item.updatedAt=at;
item.nextAction=checkpoint.nextAction;
q.updatedAt=at;
write(queuePath,q);
console.log(JSON.stringify({checkpoint:checkpointPath,repairStatus:repair.status,repairAlive:true,viteAlive:checkpoint.vite.alive,finalRender:false,uploaded:false}));
