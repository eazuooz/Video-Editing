// Select five passing originals and one passing scoped retake; retain all histories.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
const req=base+'hogwarts-observation-tts-request-v85.json',original=base+'hogwarts-observation-tts-execution-v85.json',repairReq=base+'hogwarts-tail-request-v104.json',repair=base+'hogwarts-tail-execution-v105.json',out=base+'hogwarts-observation-selected-execution-v106.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve existing selection');
const r=read(req),a=read(original),rr=read(repairReq),b=read(repair);
if(!a.endedAt||a.exitCode!==1||a.results?.length!==6||a.requestSha256!==sha(req)||!a.error.includes('scoped observation tail repair'))throw Error('Inspect original completed failure');
if(!b.endedAt||b.exitCode!==0||!b.generationComplete||!b.originalSixPreserved||b.results?.length!==1||b.results[0].id!=='hogwarts-courtyard-ui'||b.requestSha256!==sha(repairReq))throw Error('Single scoped retake must finish technically');
for(const x of [rr.sourceRequest,rr.sourceExecution,rr.sourceResearchRestoration,...rr.protectedInputs,...rr.originalSixTakeFiles])if(sha(x.path)!==x.sha256)throw Error('Protected input changed '+x.path);
const histories=[a,b].map(x=>'shared/output/gpu-handoff/'+x.leaseToken+'.json');
for(const h of histories)if(read(h).state!=='research_resume_verified')throw Error('Actual research restoration required');
const failures=a.results.filter(x=>!x.technicalTailGatePassed);
if(failures.length!==1||failures[0].id!=='hogwarts-courtyard-ui')throw Error('Repair scope changed');
const results=r.scenes.map(s=>{const record=s.id==='hogwarts-courtyard-ui'?b:a;const x=record.results.find(x=>x.id===s.id);if(!x?.technicalTailGatePassed||sha(x.path)!==x.sha256||x.sampleRate!==24000||!Number.isInteger(x.samples))throw Error('Changed or failed selected take '+s.id);return {...x,selectedFrom:s.id==='hogwarts-courtyard-ui'?repair:original,asrDirectlyReviewed:false};});
const j={schemaVersion:1,selectedAt:new Date().toISOString(),status:'six-technical-takes-selected-awaiting-whole-and-independent-ASR',requestSha256:sha(req),sourceExecutions:[ref(original),ref(repair)],repairRequest:ref(repairReq),researchRestoration:histories.map(ref),leaseToken:b.leaseToken,results,generationComplete:true,exitCode:0,endedAt:b.endedAt,originalSixPreserved:true,repairedOnly:['hogwarts-courtyard-ui'],scriptWordsChanged:false,thresholdChanged:false,wholeAsrApproved:false,independentContextAsrApproved:false,humanListeningApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,bodyRatioApproved:false,uploaded:false};
fs.writeFileSync(path.join(root,out),JSON.stringify(j,null,2)+'\n');console.log(JSON.stringify({output:out,selected:6,repairedOnly:j.repairedOnly,wholeAsrApproved:false}));
