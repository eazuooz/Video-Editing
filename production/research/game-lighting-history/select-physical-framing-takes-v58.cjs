const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:hash(p)});
const write=(p,j)=>{const target=path.join(root,p);if(fs.existsSync(target))throw Error('Preserve existing record: '+p);fs.writeFileSync(target,JSON.stringify(j,null,2)+'\n');};
const originalPath=base+'physical-framing-tts-execution-v49.json',repairPath=base+'physical-framing-tail-repair-execution-v55.json';
const original=read(originalPath),repair=read(repairPath),request=read(base+'physical-framing-tts-request-v49.json');
const histories=[original,repair].map(e=>ref('shared/output/gpu-handoff/'+e.leaseToken+'.json'));
for(const h of histories)if(read(h.path).state!=='research_resume_verified')throw Error('Research restoration not verified');
for(const f of [...request.protectedInputs,...original.results,...repair.results])if(hash(f.path)!==f.sha256)throw Error('Protected bytes changed: '+f.path);
if(!repair.generationComplete||repair.exitCode!==0||!repair.original5Preserved)throw Error('Repair incomplete');
const results=request.scenes.map(s=>{
 const previous=original.results.find(r=>r.id===s.id),replacement=repair.results.find(r=>r.id===s.id);
 const selected=previous.technicalTailGatePassed?previous:replacement;
 if(!selected?.technicalTailGatePassed)throw Error('Technical tail remains pending: '+s.id);
 return {...selected,selectedFrom:replacement===selected?repairPath:originalPath,asrDirectlyReviewed:false};
});
write(base+'physical-framing-selected-execution-v55.json',{
 schemaVersion:1,selectedAt:new Date().toISOString(),status:'five-technical-takes-selected-awaiting-complete-asr-direct-review',
 leaseToken:repair.leaseToken,sourceExecutions:[ref(originalPath),ref(repairPath)],researchRestoration:histories,
 results,allOriginalFivePreserved:true,original111Regenerated:false,generationComplete:true,
 wholeAsrApproved:false,independentContextAsrApproved:false,finalMixedAsrApproved:false,humanWholeListeningApproved:false,
});
const state=read(base+'physical-framing-asr-execution-v56.json');
if(state.completed.length!==8||state.exitCode!==0||!state.endedAt)throw Error('Eight-window worker not ended');
const findings={
 'whole-part1-overview':'All three sentences and closing 살펴보죠 are present; punctuation differences only.',
 'context-part1-overview':'Complete new overview and complete retained roadmap are present; DLSS is normalized as Latin letters. Retained roadmap must be labelled as the remaining series, rather than promised within physical part1.',
 'whole-part1-conclusion':'All sentences, retained information/cost distinction and next-part bridge are complete, ending 이어집니다.',
 'context-part1-conclusion':'Complete retained mobile conclusion plus new conclusion, with the pipeline coexistence argument and next-part bridge intact.',
 'whole-part2-conclusion':'All sentences, scarce samples, layered surfaces and visibility/reconstruction distinction are complete, ending 연결하겠습니다.',
 'context-part2-conclusion':'Complete retained development-publication caution plus conclusion. 이 절 / 2절 is an ASR orthographic ambiguity, not demonstrated PCM error.',
 'whole-part3-overview':'All sentences are present. DLSS5 is normalized as Latin letters. 맡는 / 맞는 remains a phonetic/orthographic ambiguity requiring human pronunciation review.',
 'context-part3-overview':'Complete new overview and retained DLSS4 MFG paragraph are present without invented greeting or repeated sentence. DLSS 5가지의 versus 오까지의 differs from the whole recognition and remains ambiguous; 맡는 / 맞는 is also pending human pronunciation. Last two word intervals overlap 0.14s without repeated text; use whole-window word clocks for the new scene.',
};
const windows=state.completed.map(d=>{
 if(hash(d.result)!==d.sha256)throw Error('ASR record changed');
 const r=read(d.result);return {...d,expectedCompleteTexts:r.job.sources.map(s=>s.ko),actualCompleteText:r.text,
 directFullTextCompared:true,finding:findings[d.label],sourceHashes:r.job.sources.map(s=>ref(s.path)),
 humanListeningApproved:false,pronunciationApproved:false};
});
write(base+'physical-framing-asr-direct-progress-v58.json',{
 schemaVersion:1,reviewedAt:new Date().toISOString(),state:ref(base+'physical-framing-asr-execution-v56.json'),
 directlyReadWindows:8,requiredWindows:10,windows,allFiveDirectlyReviewed:false,allFiveApproved:false,
 pendingWindows:['whole-part2-overview','context-part2-overview'],endingHeuristicUsedAsApproval:false,
 finalMixedAsrApproved:false,humanWholeListeningApproved:false,pronunciationReviewPending:true,
});
console.log('Selected4 preserved+1 repaired take; research restoration verified. Recorded8/10 directly read windows; full approval false.');
