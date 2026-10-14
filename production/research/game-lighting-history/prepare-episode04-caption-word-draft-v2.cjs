// Current111 paragraph caption preparation, with actual recognized word anchors.
// This produces no render, does not change narration, and grants no QA gate.
const fs=require('fs'),crypto=require('crypto');
const {alignNarratedEntry}=require('./episode04-caption-alignment-v1.cjs');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const assemblyPath=base+'additive-unmixed-review-assembly-v2.json',assembly=read(assemblyPath);
const anchorPath=base+'local/original-word-anchors-draft-v1.json',anchors=read(anchorPath);
if(sha(assembly.audio.path)!==assembly.audio.sha256)throw Error('Current review assembly changed');
const execution=read(base+'additive-asr-execution-v1.json');
const aliases=[...anchors.chapters[0].alignment.aliases,
 ['여덟 픽셀','8픽셀'],['네 줄','4줄'],['서른두','32'],['네 픽셀','4픽셀'],['두 줄','2줄'],['여덟 개','8개'],
 ['영과 영','0과0'],['일과 영','1과0'],['영과 일','0과1'],['이분의 일','2분의1'],['사분의 일','4분의1'],['영 점 이오','0.25'],
 ['이천십사 년','2014년'],['영 점 이','0.2'],['영 점 오','0.5'],['일 점 이오','1.25'],['영을','0을'],['일이 되어','1이되어'],
 ['한 개','1개'],['세 개','3개'],['네 개','4개'],['여섯 개','6개'],['이 곱하기 영 점 오','2곱하기0.5']
];
const paragraphs=[],cueBoundaryAdjustments=[];
for(const entry of assembly.entries){
 let draft,recognizedSource,offset;
 if(entry.kind==='preserved-original'){
  const chapter=anchors.chapters.find(c=>c.scene===entry.originalScene),p=chapter?.paragraphs.find(p=>p.id===entry.id);
  if(!p||sha(chapter.recognition.path)!==chapter.recognition.sha256)throw Error('Existing whole anchor changed: '+entry.id);
  const words=chapter.words.slice(p.wordIndices[0],p.wordIndices[1]+1);
  draft=alignNarratedEntry(entry.text,words,aliases);
  offset=entry.start+(chapter.currentOriginalSampleRange[0]-entry.originalSampleRange[0])/24000;
  recognizedSource={...chapter.recognition,wordIndices:p.wordIndices,rawWordIndices:p.rawWordIndices,excludedRawRecognitionIndices:chapter.excludedRawRecognitionIndices};
 }else{
  const completed=execution.completed.find(c=>c.label==='whole-'+entry.id);
  if(!completed||sha(completed.result)!==completed.sha256)throw Error('Completed additive whole required: '+entry.id);
  const raw=read(completed.result);draft=alignNarratedEntry(entry.text,raw.chunks,aliases);offset=entry.start;
  recognizedSource={path:completed.result,sha256:completed.sha256};
 }
 const cues=draft.cues.map(c=>({...c,sourceRecognizedSeconds:[c.from,c.to],from:Math.max(entry.start,offset+c.from),to:Math.min(entry.end,offset+c.to)}));
 for(const c of cues){
  if(c.to<=c.from)throw Error('No current caption interval: '+entry.id);
  if(c.from!==offset+c.sourceRecognizedSeconds[0]||c.to!==offset+c.sourceRecognizedSeconds[1])cueBoundaryAdjustments.push({entryId:entry.id,cue:c.id,method:'constrain-ASR-word-anchor-to-preserved-PCM-entry',originalSeconds:c.sourceRecognizedSeconds,adjustedSeconds:[c.from,c.to],humanTimingApproved:false});
 }
 for(let i=1;i<cues.length;i++)if(cues[i].from<cues[i-1].to){
  const prior=cues[i-1],current=cues[i],boundary=(prior.to+current.from)/2;
  if(boundary<=prior.from||boundary>=current.to)throw Error('Overlapping recognition requires independent diagnosis: '+entry.id);
  cueBoundaryAdjustments.push({entryId:entry.id,cues:[prior.id,current.id],method:'shared-midpoint-within-overlapping-ASR-word-times',rawEnd:prior.to,rawStart:current.from,boundary,humanTimingApproved:false});
  prior.to=boundary;current.from=boundary;
 }
 paragraphs.push({id:entry.id,kind:entry.kind,scene:entry.originalScene,paragraph:entry.paragraph??null,text:entry.text,en:entry.en,start:entry.start,end:entry.end,startSample:entry.startSample,endSample:entry.endSample,recognition:recognizedSource,alignment:draft.alignment,cues,completeOriginalWordingPreserved:true,captionWordTimesDirectlyReviewed:false,allCaptionPixelsReviewed:false});
}
if(paragraphs.length!==111)throw Error('All111 paragraphs required');
const cues=paragraphs.flatMap(p=>p.cues.map(c=>({...c,entryId:p.id,scene:p.scene}))).map((c,i)=>({...c,id:i+1}));
if(cues.some((c,i)=>i&&c.from<cues[i-1].to))throw Error('Cross-entry caption overlap');
const result={createdAt:new Date().toISOString(),assembly:{path:assemblyPath,sha256:sha(assemblyPath)},audio:assembly.audio,originalAnchors:{path:anchorPath,sha256:sha(anchorPath)},paragraphs,cues,cueBoundaryAdjustments,captionStyle:'boxed-white-forest-v1',center:[960,970],motionCanvasCenter:[0,430],fontSize:48,maxLines:2,integerFinalTimingProduced:false,allCaptionWordTimesDirectlyReviewed:false,allFinalCaptionPixelsReviewed:false,finalTimingApproved:false,finalMixedAsrApproved:false,scope:'Current111 complete Korean paragraphs, existing whole recognition, original waveform unchanged. Alignment aliases preserve original text. Raw timestamp conflicts remain explicitly recorded; independent corrected contexts and final encoded cue pixels required.'};
const path=base+'local/caption-word-draft-v2.json';fs.writeFileSync(path,JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({path,paragraphs:paragraphs.length,cues:cues.length,boundaryAdjustments:cueBoundaryAdjustments,alignment:paragraphs.map(p=>({id:p.id,editDistance:p.alignment.editDistance,cues:p.cues.length}))},null,2));
