const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const write=(p,v)=>{const dst=path.join(root,p),tmp=dst+'.writing-'+process.pid;fs.writeFileSync(tmp,JSON.stringify(v,null,2)+'\n');fs.renameSync(tmp,dst);};
const pp='projects/game-lighting-history-04/production/additive-prerequisite-encoded-pixels-v1.json',r=read(pp);
const comments=[
 '16logical pages and5resident slots; request/residence distinction and projected faces readable.',
 '4x2 input8 and8x4 output32; output cells darker but visible with labels, no FPS claim.',
 'Weighted point remains inside triangle and UV panel; equal clip-w and perspective-correction caveat visible.',
 'Same-tile teal producer/consumer and separate orange external round trip; organization and storage questions distinct.',
 'Target weights0.5, proposal probabilities0.2/0.8, corrected estimates5; mean5 and not sum10 caveat.',
 'Survival1.25 at0.8 and termination0 at0.2 recombine to expected1; deterministic removal explicitly rejected.',
 'Within-wall teal connection and red forbidden cross-window connection; proprietary DLSS predicate not claimed.',
 'Front/back labels correct, light reaches both layers, camera ray traverses front then back; historical-transparency caveat visible.',
 'Progressively reveals3 and5 generated cells after one rendered cell; fixed orange simulation tick does not multiply.',
 'Linear2 to exposure0.5 to input1 to display; illustrative curve and no exact ACES/engine formula claim.',
 'Data-flow arrows and identical COLOR/SV_Target vector confirmed; output vector overlaps teal front face and lacks contrast: repair required.'
];
r.boards.forEach((b,i)=>{if(sha(b.path)!==b.sha256)throw Error('Board changed '+b.id);b.directlyRead=true;b.readAt=new Date().toISOString();b.observation=comments[i];b.pixelIssueFound=i===10;});
r.all11BoardsDirectlyRead=true;r.wholeMovingProofsApproved=false;r.allFinalPixelsReviewed=false;
r.firstPlayback={observedStartAndIntermediate:true,observedEnded:true,endedCurrentTime:96.633333,actualPlaybackRate:1,allIntermediateMovingFramesDirectlyObserved:false,scope:'CUA video1x and all44 extracted samples; playback completion alone is not continuous direct review approval.'};
r.repair={scene:'capture-dataflow',reason:'Returned vector was rendered over same-color projected front face',source:'motion-canvas/src/projects/game-lighting-history-04/spatial/additive-prerequisite-model-v1.tsx',currentSha256:sha('motion-canvas/src/projects/game-lighting-history-04/spatial/additive-prerequisite-model-v1.tsx'),change:'Output label y240 to275 and teal to white; preserve original11-scene MP4 and source/caption timing.'};write(pp,r);
const lease=read('shared/output/GPU_HANDOFF.json'),tts=read('projects/game-lighting-history-04/production/additive-tts-execution-v1.json');
if(lease.token!=='55649b32-8197-417c-b560-cbeaa8a21ab4'||tts.leaseToken!==lease.token)throw Error('Owned actual lease required');
const cp='production/research/game-lighting-history/checkpoint.json',c=read(cp);c.updatedAt=new Date().toISOString();c.stage='episode04-24-additive-TTS-running-prerequisite-pixel-repair';
c.episode04AdditiveNarration={...c.episode04AdditiveNarration,ttsStarted:true,currentState:lease.state,actualTtsWorker:{pid:tts.actualPid,createTime:tts.createTime,command:tts.commandLine,cwd:tts.cwd},completedResearchJobEvidence:lease.completedJobEvidence,technicalTailOnly:true,researchRestoredVerified:false};
c.ownedJobsRunning=[{type:'24-addition-GPU-TTS',session:63161,workerPid:tts.actualPid,createTime:tts.createTime,command:tts.commandLine,coordinator:lease.coordinator,leaseToken:lease.token,log:lease.ttsLog,cpuThreads:2,gpuJobs:1}];c.ownedGpuJobs=1;
c.episode04PrerequisiteProof={path:pp,original11SilentScenes:true,wholeDecodeExitCode:0,all44SamplesDirectlyRead:true,repairPending:'capture-dataflow label',finalNarratedPixelsApproved:false};
c.next='Finish24 new independent TTS takes and restore original research queue; inspect actual whole/context ASR for24 additions, preserving original87 PCM. Finish one corrected proof label and retime independent models from measured narration before final native-cut/mix/ratio/render QA.';write(cp,c);
console.log(JSON.stringify({all44SamplesDirectlyRead:true,oneRepairRequired:true,actualTtsPid:tts.actualPid,state:lease.state,finalApproved:false}));
