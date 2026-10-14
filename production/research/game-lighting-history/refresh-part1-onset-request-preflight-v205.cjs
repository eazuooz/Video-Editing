// A newly reviewed foreign upload changes only our preflight binding.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/',p=b+'part1-onset-repairs-tts-request-v199.json',preflight='production/preflight/game-lighting-history-04-1.json';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
if(fs.existsSync(path.join(root,b+'part1-onset-repairs-tts-execution-v199.json'))||fs.existsSync(path.join(root,'shared/output/GPU_HANDOFF.json')))throw Error('No started state or live lease may be rebound');
const r=read(p),old=sha(p),f=read(preflight);if(f.verdict!=='distinct'||f.studioEvidence!=='production/research/game-lighting-history/part1-current-duplicate-direct-review-v204.json')throw Error('Fresh actual duplicate review required');
for(const x of r.protectedInputs)if(x.path!==preflight&&sha(x.path)!==x.sha256)throw Error('Other protected input changed '+x.path);
const backup=b+'local/part1-onset-request-before-preflight-v205.json';if(fs.existsSync(path.join(root,backup)))throw Error('Preserve historical request');fs.copyFileSync(path.join(root,p),path.join(root,backup));
const x=r.protectedInputs.find(x=>x.path===preflight);if(!x)throw Error('Missing preflight binding');const previous=x.sha256;x.sha256=sha(preflight);r.preflightRefresh={review:'production/research/game-lighting-history/part1-current-duplicate-direct-review-v204.json',previousRequest:{path:backup,sha256:old},changedOnly:preflight,previousPreflightSha256:previous,currentPreflightSha256:x.sha256,refreshedAt:new Date().toISOString(),newWorkerStarted:false};
fs.writeFileSync(path.join(root,p),JSON.stringify(r,null,2)+'\n');
fs.writeFileSync(path.join(root,b+'part1-onset-preflight-refresh-v205.json'),JSON.stringify({observedFailure:'v199 refused a changed protected preflight before synthesis/state/lease creation',request:p,previousRequestSha256:old,currentRequestSha256:sha(p),changedOnly:preflight,currentReview:r.preflightRefresh,newTtsJobStarted:false},null,2)+'\n');
console.log(JSON.stringify({preflightRebound:true,otherProtectedInputsIdentical:true,stateCreated:false}));
