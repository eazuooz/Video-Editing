const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),project='projects/game-lighting-history-03';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const cutPath=project+'/production/original-paragraph-cut-plan-v12.json';
const ttsPath=project+'/production/native-guides-tts-completion-and-research-resume-v1.json';
const requestPath=project+'/production/native-guides-tts-request-v1.json';
const out=project+'/production/measured-native-timeline-candidate-v13.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve prepared measured timeline');
const cuts=read(cutPath),tts=read(ttsPath),request=read(requestPath);
if(!cuts.allOriginalPcmSamplesPartitionedOnce||tts.observedSessionExitCode!==0||tts.results.length!==20)throw Error('Exact complete PCM required');
const extraExplanation=[34,81],guides=new Map(request.scenes.map(x=>[x.after,x]));
const slots=[];let frame=120;
for(const p of cuts.paragraphs){
 const explanation=p.retainedExplanation||extraExplanation.includes(p.index);
 slots.push({kind:'original-paragraph',id:'original-'+String(p.index).padStart(2,'0'),originalIndex:p.index,scene:p.scene,chapterIndex:p.chapterIndex,paragraphIndex:p.paragraphIndex,role:explanation?'explanation':'actual',
  frames:p.frames,fromFrame:frame,toFrame:frame+p.frames,sourceSampleRange:p.sourceSampleRange,paddingSamples:p.paddingSamples,text:p.text,
  originalExplanationPreserved:p.retainedExplanation,additionalWholeExplanation:extraExplanation.includes(p.index),sourceModel:p.sourceModel,posePair:p.posePair,motionSeconds:p.motionSeconds,
  sourceSelected:false,pixelsReviewed:false,audioJoinApproved:false});frame+=p.frames;
 const g=guides.get(p.index);if(g){
  const pcm=tts.results.find(x=>x.id===g.id);if(!pcm||sha(pcm.path)!==pcm.sha256)throw Error('Guide PCM changed');
  const frames=Math.ceil(pcm.samples/400);
  slots.push({kind:'native-guide',id:g.id,afterOriginal:p.index,scene:p.scene,chapterIndex:p.chapterIndex,role:'actual',frames,fromFrame:frame,toFrame:frame+frames,
   pcm:{path:pcm.path,sha256:pcm.sha256,samples:pcm.samples,sampleRate:pcm.sampleRate},paddingSamples:frames*400-pcm.samples,text:g.text,en:g.en,
   sourceSelected:false,pixelsReviewed:false,audioJoinApproved:false});frame+=frames;
 }
}
const totals={bodyFrames:frame-120,actualFrames:slots.filter(x=>x.role==='actual').reduce((n,x)=>n+x.frames,0),explanationFrames:slots.filter(x=>x.role==='explanation').reduce((n,x)=>n+x.frames,0),finalFrames:frame+600};
if(totals.explanationFrames!==Math.round(totals.bodyFrames*.4)||Math.abs(totals.actualFrames-totals.bodyFrames*.6)>1)throw Error('Exact measured role ratio failed');
const record={schemaVersion:1,preparedAt:new Date().toISOString(),status:'measured-PCM-candidate-not-adopted',inputHashes:[cutPath,ttsPath,requestPath].map(p=>({path:p,sha256:sha(p)})),
 introFrames:120,outroFrames:600,fps:60,sampleRate:24000,samplesPerFrame:400,slots,totals,
 originalParagraphs:84,guideParagraphs:20,originalWholeExplanationParagraphs:45,retainedWholeExplanationParagraphs:47,additionalWholeExplanationParagraphs:extraExplanation,
 bodySeconds:totals.bodyFrames/60,finalSeconds:totals.finalFrames/60,actualShare:totals.actualFrames/totals.bodyFrames,
 originalTextAndOrderPreserved:true,allOriginalPcmSamplesPreserved:true,allGuidePcmSamplesPreserved:true,guideMasterGapIncluded:false,
 sourceRate:1,loops:0,unrelatedIdleSeconds:0,sourceAudio:false,original84Regenerated:false,newMediaProduced:false,
 finalTimingApproved:false,bodyRatioApproved:false,allGuideAsrApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,rendered:false,collected:false,uploaded:false,
 rationale:'Measured raw guide PCM increases body duration. Retain all45 original planned whole explanations, and keep complete original paragraphs34 (disocclusion/history rejection) and81 (Lumen tracing/cache/update approximations) as existing projected2.5D explanations. Their678+671 frames exactly supply1349 additional explanation frames. No voice speed change, useful explanation shortening, looping or arbitrary silence quota. Actual source selection, original/guide joins and full mixed ASR remain separate gates.'};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({out,totals,bodySeconds:record.bodySeconds,finalSeconds:record.finalSeconds,additionalWholeExplanationParagraphs:extraExplanation,adopted:false}));
