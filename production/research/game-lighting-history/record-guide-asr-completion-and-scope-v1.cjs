const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const statePath=prod+'/native-guides-asr-execution-v1.json',state=read(statePath);
if(state.exitCode!==0||state.results.length!==40)throw Error('Actual complete40 result state required');
const directPath=prod+'/native-guides-asr-direct-progress-v1.json',direct=read(directPath);
if(direct.directlyReadWindows!==40||direct.allGuideAsrApproved)throw Error('Exact direct40 review and unresolved approval required');
const scopePath=prod+'/retained-clean-scoped-typecheck-v1.json';
const scope={schemaVersion:1,verifiedAt:new Date().toISOString(),command:'node motion-canvas/node_modules/typescript/bin/tsc --project production/research/game-lighting-history/local/retained-clean-tsconfig-v1.json',cwd:'D:/Github/Video-Editing',exitCode:0,
 scope:'Owned14 retained-clean scene/project modules and their model/runtime dependencies only',config:{path:'production/research/game-lighting-history/local/retained-clean-tsconfig-v1.json',sha256:sha('production/research/game-lighting-history/local/retained-clean-tsconfig-v1.json')},
 initialFailure:{exitCode:1,diagnostics:14,reason:'Missing ?scene ambient module declarations; config included nonexistent vite-env.d.ts. Corrected to actual src/env.d.ts.'},
 wholeRepositoryPassClaimed:false,newMedia:0,newImages:0,rendered:false};
if(!fs.existsSync(path.join(root,scopePath)))fs.writeFileSync(path.join(root,scopePath),JSON.stringify(scope,null,2)+'\n');
const sessionPath=prod+'/native-guides-asr-session-v1.json',session=read(sessionPath);
session.stage=state.stage;session.exitCode=0;session.actualToolSessionExit0Observed=true;session.completedWindows=40;session.finishedAt=state.finishedAt;session.processIdentityGoneObserved=true;
fs.writeFileSync(path.join(root,sessionPath),JSON.stringify(session,null,2)+'\n');
const cpPath='production/research/game-lighting-history/checkpoint.json',cp=read(cpPath),diagnosticPath=prod+'/native-guide01-padded-onset-execution-v1.json',diag=read(diagnosticPath);
cp.updatedAt=new Date().toISOString();cp.stage=diag.stage;
cp.ownedJobsRunning=[{pid:diag.actualPid,createTime:diag.createTime,commandLine:diag.command,sessionId:99415,state:diagnosticPath,cpuThreads:2,gpuJobs:0,completed:diag.results.length,total:4}];
cp.ownedActiveWork={stage:'guide01-onset-and-guide20-divergence-targeted-CPU-diagnostic',sessionId:99415,actualPid:diag.actualPid,state:diagnosticPath,cpuThreads:2,gpuJobs:0};
cp.episode03GuideAsrCompletion={path:statePath,sha256:sha(statePath),sessionId:58325,exitCode:0,actualToolSessionExit0Observed:true,windows:40,directReview:{path:directPath,sha256:sha(directPath)},allApproved:false,unresolvedGuides:['01-mesh-distance-field','20-lumen-interior-toggle']};
cp.episode03RetainedCleanScopedTypecheck={path:scopePath,sha256:sha(scopePath),exitCode:0,wholeRepositoryPass:false};
cp.episode03NativeRangeCandidate={path:prod+'/native-range-allocation-candidate-v14.json',sha256:sha(prod+'/native-range-allocation-candidate-v14.json'),actualSlots:57,nativeCuts:111,frames:55866,sourceOverlaps:0,adopted:false,continuousMotionApproved:false};
cp.next='Finish actual single CPU2 targeted diagnostics on unchanged guide01/20 PCM. Do not adopt v13/v14 or render final inputs while substantial voice mismatch is unresolved. Preserve original84 and other18 guides; any repair must be selective and use cooperative research/TTS handoff.';
fs.writeFileSync(path.join(root,cpPath),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({completedAsrWindows:40,toolExit0:true,scopedTypecheckExit0:true,currentDiagnosticPid:diag.actualPid,approved:false}));
