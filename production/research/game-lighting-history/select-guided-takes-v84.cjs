// Select completed original/repair takes; retain both histories and every WAV.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const request=base+'part3-guided-actions-tts-request-v69.json',original=base+'part3-guided-actions-tts-execution-v69.json';
const repairRequest=base+'guided-tail-repair-request-v83.json',repair=base+'guided-tail-repair-execution-v83.json';
const output=base+'part3-guided-actions-selected-execution-v84.json';
if(fs.existsSync(path.join(root,output)))throw Error('Preserve existing selected execution');
const req=read(request),a=read(original),rr=read(repairRequest),b=read(repair);
if(req.scenes.length!==37||a.results?.length!==37||!a.endedAt||a.exitCode!==1||!String(a.error).includes('observed tail failure'))throw Error('Inspect exact original completed failure');
if(!b.endedAt||b.exitCode!==0||!b.generationComplete||!b.original37Preserved||b.results?.length!==rr.scenes.length)throw Error('All scoped retakes must complete technically');
if(a.requestSha256!==sha(request)||b.requestSha256!==sha(repairRequest))throw Error('Execution request changed');
for(const x of [rr.sourceRequest,rr.sourceExecution,rr.sourceResearchRestoration,...rr.protectedInputs,...rr.original37TakeFiles])if(sha(x.path)!==x.sha256)throw Error('Protected input changed '+x.path);
const failures=new Set(a.results.filter(x=>!x.technicalTailGatePassed).map(x=>x.id));
if(failures.size!==rr.scenes.length||rr.scenes.some(x=>!failures.has(x.id)))throw Error('Repair scope differs from actual failed subset');
const histories=[a,b].map(x=>'shared/output/gpu-handoff/'+x.leaseToken+'.json');
for(const h of histories)if(read(h).state!=='research_resume_verified')throw Error('Actual research restoration not verified '+h);
const results=req.scenes.map(scene=>{
 const source=failures.has(scene.id)?b:a,file=failures.has(scene.id)?repair:original;
 const r=source.results.find(x=>x.id===scene.id);
 if(!r?.technicalTailGatePassed||r.sampleRate!==24000||!Number.isInteger(r.samples)||r.samples<=0||sha(r.path)!==r.sha256)throw Error('Selected take changed or failed '+scene.id);
 return {...r,selectedFrom:file,asrDirectlyReviewed:false};
});
const record={schemaVersion:1,selectedAt:new Date().toISOString(),status:'37-technical-takes-selected-awaiting-full-and-independent-ASR',requestSha256:sha(request),sourceExecutions:[ref(original),ref(repair)],sourceRepairRequest:ref(repairRequest),researchRestoration:histories.map(ref),leaseToken:b.leaseToken,results,generationComplete:true,exitCode:0,endedAt:b.endedAt,original111AndFiveFramingPreserved:true,original37Preserved:true,repairedOnly:rr.scenes.map(x=>x.id),scriptWordsChanged:false,thresholdChanged:false,wholeAsrApproved:false,independentContextAsrApproved:false,humanListeningApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,bodyRatioApproved:false,uploaded:false};
fs.writeFileSync(path.join(root,output),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({output,selected:results.length,repairedOnly:record.repairedOnly,wholeAsrApproved:false}));
