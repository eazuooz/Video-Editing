// Explicit sample choices from directly compared chapter-end/begin words and
// the measured PCM runs. This permits review reassembly, not audio approval.
const fs=require('fs'),crypto=require('crypto');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const anchorPath=base+'local/original-word-anchors-draft-v1.json',gapPath=base+'local/original-paragraph-gap-measurements-v1.json';
const a=read(anchorPath),g=read(gapPath),request=read(base+'additive-asr-selected-request-v4.json');
if(g.anchors.sha256!==sha(anchorPath)||a.originalAudio.sha256!==g.originalAudio.sha256)throw Error('Gap measurements must bind current anchor draft');
const choices={
 '18v:before-line-3':1258680,'18v:after-line-4':1976880,'18v:after-line-5':2308320,
 '18t:before-line-3':3826800,'18t:after-line-5':4806720,'18a:after-line-3':6600600,
 '18m:after-line-2':8293080,'18m:after-line-3':8604360,
 '19:after-line-1':9920040,'19:after-line-4':10973040,'19:after-line-6':11622960,
 '20:after-line-1':12902520,'20:after-line-5':14292120,'21m:after-line-4':16106400,
 '21a:after-line-7':19091760,'22:after-line-2':20274240,
 '22p:before-line-2':21792840,'22p:after-line-2':22148760,'22p:after-line-4':22773240,
 '22r:after-line-4':24811800
};
const cuts=request.scenes.map(s=>{
 const chapter=a.chapters.find(c=>c.scene===s.originalScene),[when,lineText]=s.position.split('-line-'),line=Number(lineText);
 const paragraph=chapter.paragraphs.find(p=>p.paragraph===line),legacy=paragraph.legacyAllocationSeconds[when==='before'?0:1];
 const atSceneBoundary=when==='before'&&line===1||when==='after'&&line===chapter.paragraphs.length;
 let sample,gap;
 if(atSceneBoundary)sample=chapter.currentOriginalSampleRange[when==='before'?0:1];
 else{
  sample=choices[s.originalScene+':'+s.position];if(!Number.isInteger(sample))throw Error('Unreviewed explicit cut: '+s.id);
  const leftId='original-'+s.originalScene+'-'+(when==='before'?line-1:line);
  const record=g.records.find(r=>r.leftId===leftId);gap=record.candidates.find(c=>c.middleSample===sample);
  if(!gap||gap.samples<960||gap.peakMax>66)throw Error('Selected actual quiet PCM run changed: '+s.id);
 }
 return {id:s.id,originalScene:s.originalScene,position:s.position,legacyEstimatedBoundarySample:Math.round(legacy*24000),selectedOriginalBoundarySample:sample,shiftFromLegacySeconds:sample/24000-legacy,originalNeighborWordsDirectlyCompared:true,measuredGap:gap??null,atPreservedOriginalSceneBoundary:atSceneBoundary,technicalBoundaryReadyForReviewReassembly:true,independentCorrectedContextApproved:false,humanListeningApproved:false};
});
if(cuts.length!==24)throw Error('Complete24 insertion mapping required');
const output={reviewedAt:new Date().toISOString(),originalAudio:a.originalAudio,anchors:{path:anchorPath,sha256:sha(anchorPath)},gapMeasurements:{path:gapPath,sha256:sha(gapPath)},selectedRequest:{path:base+'additive-asr-selected-request-v4.json',sha256:sha(base+'additive-asr-selected-request-v4.json')},cuts,scope:'Correct legacy character-weighted paragraph allocations using observed last/first words and original PCM quiet runs. Preserve original87 PCM/new24 takes; no voice or final-mix approval.',all24TechnicalBoundariesReadyForReviewReassembly:true,allCorrectedIndependentContextsApproved:false,finalTimingApproved:false,finalMixedAsrApproved:false,humanWholeListeningApproved:false};
const p=base+'additive-splice-boundary-review-v2.json';if(fs.existsSync(p))throw Error('Existing explicit review preserved');fs.writeFileSync(p,JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify(cuts.map(c=>({id:c.id,originalBoundary:c.selectedOriginalBoundarySample,shiftSeconds:c.shiftFromLegacySeconds,quietPeak:c.measuredGap?.peakMax})),null,2));
