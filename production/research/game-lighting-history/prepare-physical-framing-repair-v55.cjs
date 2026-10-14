const fs=require('node:fs'),crypto=require('node:crypto');
const base='projects/game-lighting-history-04/production/',script='projects/game-lighting-history-04/script/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write=(p,j)=>{if(fs.existsSync(p))throw Error('Preserve existing '+p);fs.writeFileSync(p,JSON.stringify(j,null,2)+'\n')};
const sourceRequest=base+'physical-framing-tts-request-v49.json',sourceExecution=base+'physical-framing-tts-execution-v49.json';
const request=read(sourceRequest),execution=read(sourceExecution),history='shared/output/gpu-handoff/'+execution.leaseToken+'.json',lease=read(history);
if(execution.exitCode!==1||execution.results.length!==5||lease.state!=='research_resume_verified')throw Error('Inspect final five takes and actual restoration first');
const failed=execution.results.filter(r=>!r.technicalTailGatePassed);
if(failed.length!==1||failed[0].id!=='part2-overview')throw Error('Repair only the observed failure');
for(const f of request.protectedInputs)if(sha(f.path)!==f.sha256)throw Error('Protected input changed '+f.path);
for(const f of execution.results)if(sha(f.path)!==f.sha256)throw Error('Original take changed '+f.path);
const ko=read(script+'physical-part-framing.ko.v45.json'),en=read(script+'physical-part-framing.en.v45.json');
const ids=new Set(failed.map(r=>r.id)),newKo=structuredClone(ko),newEn=structuredClone(en);
newKo.scenes=ko.scenes.filter(s=>ids.has(s.id));newEn.scenes=en.scenes.filter(s=>ids.has(s.id));
if(newKo.scenes.length!==1||newEn.scenes.length!==1||newKo.scenes[0].lines.join(' ')!==request.scenes.find(s=>ids.has(s.id)).ko)throw Error('Preserve whole paired wording');
const koPath=script+'physical-framing-tail.ko.v55.json',enPath=script+'physical-framing-tail.en.v55.json';
write(koPath,newKo);write(enPath,newEn);
const manifest=read(request.manifestOverride),dir='shared/output/narration/game-lighting-history-04/qwen3-1.7b-physical-framing-tail-v55',stem='game-lighting-history-04-physical-framing-tail-v55';
manifest.paths.script=koPath;manifest.paths.scriptEn=enPath;manifest.tts.outputDir=dir;manifest.tts.filenameStem=stem;manifest.tts.maxRenderAttempts=5;
manifest.paths.narration=dir+'/'+stem+'.wav';manifest.paths.captionsKo=dir+'/'+stem+'.srt';manifest.paths.captionsEn=dir+'/'+stem+'.en.srt';
manifest.physicalFramingScope={newScenes:1,original111Regenerated:false,passingFourRegenerated:false,failedId:failed[0].id,technicalThresholdsUnchanged:true};
const manifestPath=base+'physical-framing-tail-manifest-v55.json';write(manifestPath,manifest);
const out=base+'physical-framing-tail-repair-request-v55.json';
write(out,{schemaVersion:1,preparedAt:new Date().toISOString(),sourceRequest:{path:sourceRequest,sha256:sha(sourceRequest)},sourceExecution:{path:sourceExecution,sha256:sha(sourceExecution)},restoredHistory:{path:history,sha256:sha(history)},protectedInputs:[...request.protectedInputs,...[koPath,enPath,manifestPath].map(path=>({path,sha256:sha(path)}))],original5TakeFiles:execution.results.map(r=>({path:r.path,sha256:r.sha256})),manifestOverride:manifestPath,scenes:request.scenes.filter(s=>ids.has(s.id)).map(s=>({...s,path:dir+'/chunks/'+s.id+'-scene.wav'})),preserveOriginal111:true,preservePassingFour:true,technicalThresholdsUnchanged:true,wholeAsrRequired:true,independentContextAsrRequired:true,researchRestoreRequired:true});
let worker=fs.readFileSync('production/research/game-lighting-history/render-episode04-additive-tail-repair-v2.py','utf8');
worker=worker.replace('Cooperative exclusive TTS of observed failed additions, preserving all24.','Cooperative repair of the one observed failed framing take; preserve111+5.')
 .replaceAll('additive-tail-repair-request-v2.json','physical-framing-tail-repair-request-v55.json').replaceAll('additive-tail-repair-execution-v2.json','physical-framing-tail-repair-execution-v55.json')
 .replace('len(request[\'scenes\'])>=24','len(request[\'scenes\'])>=5').replaceAll('original24TakeFiles','original5TakeFiles').replaceAll('original24Preserved','original5Preserved')
 .replace("['node','scripts/review-video-duplicates.cjs'","['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe','scripts/review-video-duplicates.cjs'");
const workerPath='production/research/game-lighting-history/render-physical-framing-tail-repair-v55.py';
if(fs.existsSync(workerPath))throw Error('Preserve existing worker');fs.writeFileSync(workerPath,worker);
const checkpointPath='production/research/game-lighting-history/checkpoint.json',c=read(checkpointPath);
c.updatedAt=new Date().toISOString();c.episode04PhysicalFramingRepairV55={request:out,worker:workerPath,failedIds:[failed[0].id],previousWorkerEnded:true,previousResearchRestoredVerified:true,researchHistory:history,status:'prepared-not-started',actualNewTakes:0,original111Regenerated:false,passingFourRegenerated:false,wholeAsrApproved:false,finalMixedAsrApproved:false,uploaded:false};
fs.writeFileSync(checkpointPath,JSON.stringify(c,null,2)+'\n');console.log('Prepared exactly one scoped retake; no synthesis');
