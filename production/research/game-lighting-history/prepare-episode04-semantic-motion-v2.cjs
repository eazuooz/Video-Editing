// Prepared word-bound motion data. No scene/render/audio/ratio approval.
const fs=require('fs'),crypto=require('crypto');
const {alignOriginalCharacters}=require('./episode04-caption-alignment-v1.cjs');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const path=base+'local/caption-word-draft-v2.json',captions=read(path),assembly=read(captions.assembly.path);
if(sha(captions.assembly.path)!==captions.assembly.sha256)throw Error('Current assembly changed');
const original=read(captions.originalAnchors.path);
const groups={overview:['seriesSynthesis',0], '18v':['vsm',0], '18t':['upscaling',0], '18a':['visibility',0], '18m':['mobile',0], '19':['pathBudget',0], '20':['reconstruction',0], '21m':['megalights',0], '21a':['transparency',0], '22':['dlssLatest',0], '22p':['postprocess',0], '22r':['frameInspection',0], '22rb':['frameInspection',8], conclusion:['seriesSynthesis',1]};
const prerequisites={'02-pre-vsm-address':'vsm-address','05-pre-upscaling-grid':'upscaling-grid','07-pre-visibility-interpolation':'visibility-interpolation','08-pre-mobile-local-memory':'mobile-local-memory','11-pre-path-probability':'path-probability','12-pre-path-survival':'path-survival','13-pre-reconstruction-boundary':'reconstruction-boundary','16-pre-direct-versus-transparent':'direct-versus-transparent','18-pre-generated-frame-count':'generated-frame-count','20-pre-display-transform':'display-transform','23-pre-capture-dataflow':'capture-dataflow'};
// Progress landmarks are taken from the actual model's changes, not from
// character counts or a whole-paragraph proportional clock. Hold between beats.
const landmarks={
 'original-overview-1':[0,.72,1,1],
 'original-18v-1':[.45,1,1], 'original-18v-2':[.2,.55,1],
 'original-18v-3':[.15,1,1], 'original-18v-4':[0,1,1],
 'original-18v-5':[.35,.7,1], 'original-18v-6':[0,1,1], 'original-18v-7':[.25,1,1],
 'original-18t-1':[0,1], 'original-18t-2':[1,1,1], 'original-18t-3':[.49,.5,1],
 'original-18t-4':[.75,.9,1], 'original-18t-5':[.85,1,1], 'original-18t-6':[0,1,1], 'original-18t-7':[1,1],
 'original-18a-1':[0,.1,1], 'original-18a-2':[.35,1,1], 'original-18a-3':[0,1,1], 'original-18a-4':[0,.1,1], 'original-18a-5':[.8,1], 'original-18a-6':[1,1,1],
 'original-18m-1':[0,.6,1], 'original-18m-2':[0,.6,1], 'original-18m-3':[.5,1], 'original-18m-4':[.49,.5,1], 'original-18m-5':[.5,1], 'original-18m-6':[.6,1],
 'original-19-1':[.7,1,1], 'original-19-2':[1,1,1], 'original-19-3':[.35,.7,1], 'original-19-4':[.3,.55,1,1], 'original-19-5':[.5,1,1], 'original-19-6':[0,.4,1], 'original-19-7':[.4,.7,1], 'original-19-8':[.25,1,1], 'original-19-9':[0,1,1],
 'original-20-1':[0,.5,1], 'original-20-2':[.45,.8,1], 'original-20-3':[.55,1], 'original-20-4':[0,1,1], 'original-20-5':[.25,.8,1], 'original-20-6':[0,.7,1],
 'original-21m-1':[.4,1], 'original-21m-2':[.3,.75,1], 'original-21m-3':[.35,.8,1], 'original-21m-4':[.25,.8,1], 'original-21m-5':[.7,1,1], 'original-21m-6':[.6,1,1],
 'original-21a-1':[.1,.7,1], 'original-21a-2':[1,1,1], 'original-21a-3':[0,0,.5,1,1], 'original-21a-4':[.3,1,1], 'original-21a-5':[0,1,1], 'original-21a-6':[.6,.8,1], 'original-21a-7':[.7,1,1], 'original-21a-8':[.3,.7,1],
 'original-22-1':[1,1,1], 'original-22-2':[0,1,1], 'original-22-3':[.2,.8,1], 'original-22-4':[.8,1,1], 'original-22-5':[.7,1,1],
 'original-22p-1':[0,.3,1], 'original-22p-2':[.2,.85,1], 'original-22p-3':[.3,.8,1], 'original-22p-4':[.35,.7,1], 'original-22p-5':[.1,.3,1], 'original-22p-6':[.7,1],
 'original-22r-1':[0,.1,1], 'original-22r-2':[0,.8,1], 'original-22r-3':[0,.8,1], 'original-22r-4':[.4,.8,1], 'original-22r-5':[.1,.65,1], 'original-22r-6':[.5,.8,1], 'original-22r-7':[.3,.8,1], 'original-22r-8':[.3,.8,1],
 'original-22rb-1':[.1,.8,1], 'original-22rb-2':[.1,.8,1], 'original-22rb-3':[.3,.8,1], 'original-22rb-4':[.3,.8,1], 'original-22rb-5':[0,.3,1], 'original-22rb-6':[.2,.8,1], 'original-22rb-7':[.3,.8,1],
 'original-conclusion-1':[1,1], 'original-conclusion-2':[0,1,1], 'original-conclusion-3':[0,.8,1], 'original-conclusion-4':[0,.8,1], 'original-conclusion-5':[.4,1],
 '02-pre-vsm-address':[0,.25,.25,1], '05-pre-upscaling-grid':[0,.39,.74,1],
 '07-pre-visibility-interpolation':[0,.59,.9,1,1], '08-pre-mobile-local-memory':[0,0,1],
 '11-pre-path-probability':[0,.3,.35,.63,.84,1], '12-pre-path-survival':[0,.44,1,1],
 '13-pre-reconstruction-boundary':[0,.7,1], '16-pre-direct-versus-transparent':[.4,1,1,1],
 '18-pre-generated-frame-count':[0,.5,1,1], '20-pre-display-transform':[0,.49,.49,1],
 '23-pre-capture-dataflow':[.44,.8,1,1],
};
const paragraphs=[],adjustments=[];
for(const p of captions.paragraphs){
 const entry=assembly.entries.find(e=>e.id===p.id);let words,offset;
 if(p.kind==='preserved-original'){
  const chapter=original.chapters.find(c=>c.scene===p.scene);
  words=chapter.words.slice(p.recognition.wordIndices[0],p.recognition.wordIndices[1]+1);
  offset=entry.start+(chapter.currentOriginalSampleRange[0]-entry.originalSampleRange[0])/24000;
 }else{if(sha(p.recognition.path)!==p.recognition.sha256)throw Error('Additive result changed');words=read(p.recognition.path).chunks;offset=p.start;}
 const aligned=alignOriginalCharacters(p.text,words,p.alignment.aliases);
 const sentences=p.text.match(/[\s\S]+?(?:[.!?](?=\s|$)|$)/g).filter(s=>s.trim());
 if(p.id==='18-pre-generated-frame-count'){
  const at=sentences[1].indexOf('다섯 개를');if(at<0)throw Error('Exact generated-frame numeric phrase required');
  sentences.splice(1,1,sentences[1].slice(0,at),sentences[1].slice(at));
 }
 const targets=landmarks[p.id];
 if(p.kind!=='observation-guide'&&(!targets||targets.length!==sentences.length))throw Error('Explicit semantic landmarks required: '+p.id+' sentences '+sentences.length);
 let at=0,prior=0;const stages=[];
 for(const [i,s] of sentences.entries()){
  const literal=s.trim(),from=p.text.indexOf(literal,at),to=from+literal.length;at=to;
  const matched=aligned.matching.filter((w,j)=>w!==null&&aligned.original.map[j]>=from&&aligned.original.map[j]<to);
  if(!matched.length)throw Error('No actual word anchor: '+p.id);
  const lo=Math.min(...matched),hi=Math.max(...matched);
  let begin=Math.max(p.start,offset+words[lo].timestamp[0]),end=Math.min(p.end,offset+words[hi].timestamp[1]);
  if(stages.length&&begin<stages.at(-1).to){const previous=stages.at(-1),boundary=(previous.to+begin)/2;adjustments.push({entry:p.id,sentences:[i,i+1],old:[previous.to,begin],boundary,reason:'shared midpoint in overlapping recognition word times',humanTimingApproved:false});previous.to=boundary;begin=boundary;}
  if(end<=begin)throw Error('Motion anchor interval invalid');
  const next=targets?.[i]??null;
  stages.push({sentence:i+1,anchor:literal,sourceCharacters:[from,to],rawWordIndices:[lo,hi],sourceWordSeconds:[words[lo].timestamp[0],words[hi].timestamp[1]],from:begin,to:end,progressFrom:targets?prior:null,progressTo:next,wordTimesDirectlyReviewed:false,renderedPixelsReviewed:false});prior=next;
 }
 const group=groups[p.scene];
 const model=p.kind==='prerequisite'?'prerequisite':p.kind==='observation-guide'?'native-observation':group?.[0];
 if(!model)throw Error('Scene-specific model required');
 paragraphs.push({id:p.id,kind:p.kind,model,mode:p.kind==='preserved-original'?group[1]+p.paragraph-1:null,prerequisiteId:prerequisites[p.id]??null,from:p.start,to:p.end,text:p.text,stages,sourceRecognition:p.recognition,wholeContextCompared:false,semanticMotionDirectlyReviewed:false,integerTimingProduced:false});
}
const result={createdAt:new Date().toISOString(),scope:'111 independent paragraph motion/observation drafts bound to current unchanged PCM. Semantic sentence landmarks follow each actual model phase; native observation sentences need object-tracked overlays and selected cuts. No scenes instantiated, ratio/timing/mix/pixel/human approval granted.',captionDraft:{path,sha256:sha(path)},assembly:captions.assembly,audio:captions.audio,paragraphs,adjustments,all111WordStagesDirectlyReviewed:false,all24CorrectedContextsApproved:false,finalTimingApproved:false,finalMixedAsrApproved:false,allFinalPixelsReviewed:false};
const out=base+'local/semantic-motion-draft-v2.json';fs.writeFileSync(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({path:out,paragraphs:paragraphs.length,stages:paragraphs.reduce((n,p)=>n+p.stages.length,0),adjustments:adjustments.length,approved:false}));
