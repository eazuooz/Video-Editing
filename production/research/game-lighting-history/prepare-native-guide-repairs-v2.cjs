const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),project='projects/game-lighting-history-03',prod=project+'/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),write=(p,x)=>{if(fs.existsSync(path.join(root,p)))throw Error('Preserve existing '+p);fs.writeFileSync(path.join(root,p),JSON.stringify(x,null,2)+'\n');};
const oldRequest=read(prod+'/native-guides-tts-request-v1.json'),oldTts=read(prod+'/native-guides-tts-execution-v1.json'),diagnosticPath=prod+'/native-guide01-padded-onset-execution-v1.json',diagnostic=read(diagnosticPath);
if(diagnostic.exitCode!==0||diagnostic.results.length!==4)throw Error('Completed targeted PCM diagnostics required');
const scenes=oldRequest.scenes.filter(x=>['01-mesh-distance-field','20-lumen-interior-toggle'].includes(x.id)).map(x=>({...x}));
const last=scenes[1];last.previousKo=last.text;last.previousEn=last.en;
last.text=last.text.replace('루멘 글로벌 일루미네이션 항목을 바꾸는 동작을 확인하고, 밝은 창문 가까운 곳과 소파 뒤쪽의 벽과 천장을 나누어 보겠습니다.','밝은 창문 가까운 곳과 소파 뒤쪽의 벽, 그리고 천장을 나누어 보겠습니다.');
last.en=last.en.replace('Identify the edit to Lumen Global Illumination, then inspect the region near the bright windows separately from the wall behind the sofa and the ceiling.','Inspect the region near the bright windows separately from the wall behind the sofa and the ceiling.');
if(last.text===last.previousKo||last.en===last.previousEn)throw Error('Exact narrowed observation edit required');
const split=t=>t.match(/[^.!?]+[.!?]+/g)?.map(x=>x.trim())??[];
for(const x of scenes){x.lines=split(x.text);x.enLines=split(x.en);if(x.lines.length!==({ '01-mesh-distance-field':6,'20-lumen-interior-toggle':7 })[x.id]||x.enLines.length!==x.lines.length)throw Error('Complete independent sentence pairing required');x.path='shared/output/narration/game-lighting-history-03/qwen3-1.7b-native-guide-repairs-v2/'+x.id+'-joined.wav';}
const koPath=project+'/script/native-guide-repairs.ko.v2.json',enPath=project+'/script/native-guide-repairs.en.v2.json';
write(koPath,{scenes:scenes.map(x=>({id:x.id,title:x.id,lines:x.lines}))});write(enPath,{scenes:scenes.map(x=>({id:x.id,title:x.id,lines:x.enLines}))});
const manifest=read(prod+'/native-guides-tts-manifest-v1.json');manifest.paths.script=koPath;manifest.tts.outputDir='shared/output/narration/game-lighting-history-03/qwen3-1.7b-native-guide-repairs-v2';manifest.tts.filenameStem='native-guide-repairs-v2';manifest.tts.renderMode='line';manifest.tts.lineGapSeconds=.28;
const manifestPath=prod+'/native-guide-repairs-tts-manifest-v2.json';write(manifestPath,manifest);
const reviewPath=prod+'/native-guide-repairs-script-review-v2.json';
write(reviewPath,{schemaVersion:1,reviewedAt:new Date().toISOString(),scope:'Two unresolved, unapproved guide candidates only; original84 and other18 guides preserved',diagnostic:{path:diagnosticPath,sha256:sha(diagnosticPath)},
 directReadDiagnosticTexts:diagnostic.results.map(x=>({label:x.label,actualFullText:x.text})),
 findings:['Guide01 missing 지금 remains after silence-padded first-two-sentence and complete-guide decodes; no recognizer-only approval.','Guide20 first12seconds remains unrelated 블루프린트/재생 text; middle12seconds yields unrelated greeting with sparse timestamps. Two full decodes and targeted windows are insufficient for approval. Regenerate conservatively; do not claim that the recognized greeting proves an actual spoken greeting.','At native Lumen668.5/670s, the original presenter overlay covers the left portion of the lower LightingFeatures menu, and the presenter-free viewport crop omits that lower menu. The revised guide describes the directly observed bright/dark interior and camera movement without claiming to read the exact hidden LumenGI menu item.'],
 revisedScenes:scenes.map(x=>({id:x.id,ko:x.text,en:x.en,lines:x.lines,enLines:x.enLines})),fullKoEnDirectlyReviewed:true,completeSentenceCount:13,approvedForMeasurementOnly:true,audioApproved:false,humanListening:'pending',humanPronunciation:'pending',sourceMotionFullApproval:false,
 invalidatedCandidates:['measured-native-timeline-candidate-v13.json','native-range-allocation-candidate-v14.json','retained-clean-scene-preparation-v1.json'],reason:'Repaired PCM durations must replace only these2 guide candidates and retime final mix, roles, scenes, both SRTs and chapters together.'});
const protect=new Map(oldRequest.protectedInputs.map(x=>[x.path,x.sha256]));
for(const p of [prod+'/native-guides-tts-request-v1.json',prod+'/native-guides-tts-execution-v1.json',diagnosticPath,koPath,enPath,manifestPath,reviewPath])protect.set(p,sha(p));
for(const x of oldTts.results)protect.set(x.path,x.sha256);
const requestPath=prod+'/native-guide-repairs-tts-request-v2.json';write(requestPath,{schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-03',manifestOverride:manifestPath,scriptReview:reviewPath,scenes,expectedSentenceChunks:13,protectedInputs:[...protect].map(([path,sha256])=>({path,sha256})),
 preserveOriginal84:true,preserveOther18GuidePcm:true,preserveFailedCandidates:true,rendered:false,audioApproved:false});
console.log(JSON.stringify({requestPath,scenes:scenes.map(x=>({id:x.id,ko:x.text,en:x.en,sentences:x.lines.length})),sentenceChunks:13,newMedia:0}));
