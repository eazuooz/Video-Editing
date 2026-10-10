const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),project='projects/game-lighting-history-03',base='production/research/game-lighting-history';
const read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const source='motion-canvas/src/projects/game-lighting-history-03/spatial/narrated-data-v3.json',planPath=project+'/production/native-integration-plan-v11.json';
const d=read(source),plan=read(planPath),out=project+'/production/original-paragraph-cut-plan-v12.json';
if(fs.existsSync(path.join(root,out)))throw Error('Preserve prepared cut plan');
for(const x of plan.inputHashes)if(sha(x.path)!==x.sha256)throw Error('Original input changed');
const flat=[];let index=0;
for(let chapterIndex=0;chapterIndex<d.chapters.length;chapterIndex++){
 const c=d.chapters[chapterIndex];
 for(let paragraphIndex=0;paragraphIndex<c.paragraphs.length;paragraphIndex++){
  const p=c.paragraphs[paragraphIndex],old=plan.paragraphs[index++],cues=c.cues.filter(q=>q.paragraph===p.index);
  if(p.originalKo!==old.text||c.scene!==old.scene||!cues.length)throw Error('Exact paragraph content or cues changed');
  flat.push({index,chapterIndex,paragraphIndex,scene:c.scene,text:p.originalKo,chapterSourceFrom:c.sourceFrom,
   firstCue:{from:c.sourceFrom+cues[0].from,text:cues[0].text},lastCue:{to:c.sourceFrom+cues.at(-1).to,text:cues.at(-1).text},
   oldEstimatedFrom:old.originalFromFrame,oldEstimatedTo:old.originalToFrame,retainedExplanation:plan.explanationRetention.paragraphs.includes(index),
   sourceModel:c.model,posePair:p.pair,motionSeconds:p.move.map(t=>c.sourceFrom+t),earlyRay:p.earlyRay??null});
 }
}
if(flat.length!==84)throw Error('Expected all original84 paragraphs');
const boundaries=[{sample:0,seconds:0,frame:0,kind:'original-PCM-start'}];
for(let i=1;i<flat.length;i++){
 const prev=flat[i-1],next=flat[i],chapterBoundary=prev.chapterIndex!==next.chapterIndex;
 if(prev.lastCue.to>next.firstCue.from+.0001)throw Error('Overlapping paragraph speech anchors '+next.index);
 const sample=Math.round((prev.lastCue.to+next.firstCue.from)/2*24000),seconds=sample/24000,frame=Math.round(seconds*60);
 if(seconds<prev.lastCue.to-.0001||seconds>next.firstCue.from+.0001)throw Error('Sample cut falls outside recognized interparagraph gap '+next.index);
 boundaries.push({sample,frame,seconds,kind:chapterBoundary?'midpoint-of-preserved-original-interchapter-gap':'midpoint-between-complete-paragraph-word-cues',previousIndex:prev.index,nextIndex:next.index,
  lastSpokenEnd:prev.lastCue.to,nextSpokenStart:next.firstCue.from,lastText:prev.lastCue.text,nextText:next.firstCue.text,
  leadMarginSeconds:seconds-prev.lastCue.to,followingMarginSeconds:next.firstCue.from-seconds,zeroRecognizedGap:next.firstCue.from-prev.lastCue.to<.001});
}
const timing=read(plan.inputHashes.find(x=>x.path.endsWith('.timing.json')).path),samples=Math.round(timing.duration_seconds*timing.sample_rate),frames=Math.ceil(samples/timing.sample_rate*60);
boundaries.push({sample:samples,seconds:samples/24000,frame:frames,kind:'ceil-final-partial-frame-to-preserve-every-original-PCM-sample',originalSamples:samples});
const paragraphs=flat.map((x,i)=>({...x,originalFromFrame:boundaries[i].frame,originalToFrame:boundaries[i+1].frame,
  frames:Math.ceil((boundaries[i+1].sample-boundaries[i].sample)/400),sourceSampleRange:[boundaries[i].sample,boundaries[i+1].sample],
  paddingSamples:Math.ceil((boundaries[i+1].sample-boundaries[i].sample)/400)*400-(boundaries[i+1].sample-boundaries[i].sample),
  allOriginalTextPreserved:true,cutDirectlyReviewed:false}));
if(timing.sample_rate!==24000||paragraphs.some((x,i)=>!i?x.sourceSampleRange[0]!==0:x.sourceSampleRange[0]!==paragraphs[i-1].sourceSampleRange[1])||paragraphs.at(-1).sourceSampleRange[1]!==samples)throw Error('Lossless source partition failed');
const retained=paragraphs.filter(x=>x.retainedExplanation).reduce((n,x)=>n+x.frames,0);
const record={schemaVersion:1,preparedAt:new Date().toISOString(),inputHashes:[source,planPath,...plan.inputHashes.map(x=>x.path)].map(x=>({path:x,sha256:sha(x)})),paragraphs,boundaries,
 originalParagraphs:84,originalContinuousFrames:frames,originalFrames:paragraphs.reduce((n,x)=>n+x.frames,0),originalSamples:samples,retainedWholeExplanationParagraphs:45,retainedExplanationFrames:retained,
 minimumBodyFrames:Math.ceil(retained/.4),minimumAddedActualFrames:Math.ceil(retained/.4)-paragraphs.reduce((n,x)=>n+x.frames,0),
 originalTextAndOrderPreserved:true,allOriginalPcmSamplesPartitionedOnce:true,actualPcmSpliced:false,
 estimatedTimingPreservedAsHistorical:true,guideInserted:false,allCutsDirectlyReviewed:false,finalTimingApproved:false,finalMixedAsrApproved:false,
 zeroRecognizedGapBoundaries:boundaries.filter(x=>x.zeroRecognizedGap),assembledJoinReviewRequired:true,
 reason:'Earlier native plan used proportional pre-ASR paragraph timestamps; those unadopted boundaries differ from complete-word cues. Sample-accurate cuts use reviewed whole-ASR word intervals, with separate frame-ceil slots and silence padding smaller than one frame per paragraph. Preserve every original sample and all45 complete explanations. Zero-gap recognized boundaries require explicit PCM/join review; recognition timestamps alone do not approve an audio edit.'};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({out,originalSamples:samples,originalFrames:frames,retainedExplanationFrames:retained,minimumAddedSeconds:record.minimumAddedActualFrames/60,actualPcmSpliced:false}));
