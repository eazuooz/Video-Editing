// Observe the owned followup without changing protected audio or research controls.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const exists=p=>fs.existsSync(path.join(root,p));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const originalPath=base+'part3-guided-actions-tts-execution-v69.json',original=read(originalPath);
const originalHistory='shared/output/gpu-handoff/'+original.leaseToken+'.json';
const resumed=process.argv.includes('--resume');
const executionPath=base+(resumed?'guided-followup-resume-execution-v92.json':'guided-followup-batch-execution-v87.json');
const active=exists('shared/output/GPU_HANDOFF.json')?read('shared/output/GPU_HANDOFF.json'):null;
const execution=exists(executionPath)?read(executionPath):null;
const output=base+(resumed?'guided-followup-resume-progress-v93.json':'guided-followup-progress-v90.json');
let token=execution?.leaseToken;
const runner=resumed?'render-guided-followup-resume-v92.py':'render-guided-followup-batch-v87.py';
if(!token&&active?.project==='game-lighting-history-04'&&active?.ttsCommand?.some(s=>s.endsWith(runner)))token=active.token;
if(!token&&exists(output)){
 const saved=read(output),p='shared/output/gpu-handoff/'+saved.leaseToken+'.json';
 if(exists(p)){const h=read(p);if(h.project==='game-lighting-history-04'&&h.ttsCommand?.some(s=>s.endsWith(runner)))token=h.token;}
}
if(!token)throw Error('No actual owned followup handoff found');
const historyPath='shared/output/gpu-handoff/'+token+'.json',history=read(historyPath);
const record={schemaVersion:1,observedAt:new Date().toISOString(),status:execution?.status||history.state,sessionId:resumed?84952:70822,originalBatch:ref(originalPath),originalResults:original.results.length,observedFailedOnly:original.results.filter(x=>!x.technicalTailGatePassed).map(x=>x.id),originalResearchRestoration:{...ref(originalHistory),state:read(originalHistory).state},followupExecution:execution?ref(executionPath):null,followupHistory:ref(historyPath),leaseToken:token,coordinator:history.coordinator,ttsOwner:history.ttsOwner||null,modelWorker:execution?.actualIdentity||null,currentChild:execution?.currentChild||null,boundaryStatus:history.boundaryStatus||null,ttsLog:history.ttsLog||null,completedChildJobs:execution?.jobs||[],followupGenerationComplete:execution?.generationComplete===true,researchRestorationObserved:history.state==='research_resume_verified',cpuThreads:execution&&!execution.endedAt?2:0,gpuJobs:history.state==='tts_running'?1:0,wholeAsrApproved:false,independentContextAsrApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,bodyRatioApproved:false,collected:false,uploaded:false,next:'Verify four scoped retakes and six new observations, actual research restoration, selected37+6 PCM; directly compare86 whole/context ASR windows before current native allocation/final production.'};
record.preModelFailure=execution===null&&history.ttsExitCode===1;
record.actualTtsExitCode=history.ttsExitCode??null;
if(record.preModelFailure){record.status='pre-model-current-inventory-check-failed; research-restored';record.next='Read changed inventory text and refresh its content review, then resume only the still-unstarted four retakes and six observation takes.';}
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json',checkpoint=read(cp);
checkpoint[resumed?'episode04GuidedFollowupResumeV92':'episode04GuidedFollowupV87']={record:output,status:record.status,sessionId:record.sessionId,leaseToken:token,coordinator:record.coordinator,worker:record.modelWorker,currentChild:record.currentChild,cpuThreads:record.cpuThreads,gpuJobs:record.gpuJobs,generationComplete:record.followupGenerationComplete,researchRestorationObserved:record.researchRestorationObserved,next:record.next};
checkpoint.updatedAt=record.observedAt;
const tmp=path.join(root,cp+'.observing-'+process.pid);fs.writeFileSync(tmp,JSON.stringify(checkpoint,null,2)+'\n');fs.renameSync(tmp,path.join(root,cp));
console.log(JSON.stringify({output,status:record.status,leaseToken:token,completedChildren:record.completedChildJobs.length,researchRestorationObserved:record.researchRestorationObserved,uploaded:false}));
