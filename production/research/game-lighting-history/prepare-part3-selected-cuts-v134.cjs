const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,'')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'),ref=p=>({path:p,sha256:sha(p)});
const out=b+'selected-part3-source-plan-v134.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve previous plan');
const g=read('projects/game-lighting-history-04/script/physical-part3-guided-actions.koen.v69.json'),h=read('projects/game-lighting-history-04/script/physical-part3-hogwarts-observation.koen.v81.json'),fresh=read('projects/game-lighting-history-04/script/native-followup.koen.v120.json'),onset=read('projects/game-lighting-history-04/script/native-onset.koen.v128.json');
const selected=[...read(b+'part3-guided-actions-selected-execution-v84.json').results,...read(b+'hogwarts-observation-selected-execution-v106.json').results];
const takes=new Map(selected.map(t=>[t.id,t]));
for(const t of read(b+'native-followup-selected-v126.json').results)takes.set(t.id,t);
for(const t of read(b+'native-onset-execution-v128.json').results)takes.set(t.id,t);
const texts=new Map([...g.scenes,...h.scenes].map(s=>[s.id,{...s}]));
for(const s of fresh.scenes)texts.set(s.id,{...s});for(const s of onset.scenes)texts.set(s.id,{...s});
const changes={
 'appearance-resident':[[5.5,21]],'appearance-starfield':[[5.5,21.5]],'appearance-hogwarts':[[6,23.5]],'appearance-nba':[[13,24.8],[27,39],[40,47]],
 'exposure-context':[[1567.6,1586]],'exposure-after-limit':[[1602.88,1621]],
 'histogram-open':[[1637.5,1657.5]],'histogram-log-scale':[[1657.5,1677]],'histogram-camera-condition':[[1677,1696]],'histogram-control-result':[[1696,1715]],
 'grade-channel-controls':[[1855,1872.5]],'grade-shared-reference':[[1872.5,1890.3]],'grade-to-lookup':[[1890.3,1911]],
 'focus-legend-context':[[2317.7,2330],[2336.02,2349]],'focus-distance-transition':[[2349,2369]],'focus-normal-return':[[2470,2486.166666666667]],'focus-error-isolation':[[2380.1,2397.633333333333]],
 'capture-target-view':[[48,67]],'capture-position-input':[[67,89.8]],'capture-stage-selection':[[89.8,109.52]]
};
const explanation=new Set(['appearance-prerequisite','appearance-to-controls','focus-later-settings','focus-observation-protocol','focus-to-frame-inspection']);
const sources={...g.sources,...h.sources,...fresh.sources};
const intervals=new Map(),rows=[];
for(const [id,s] of texts){
 const t=takes.get(id);if(!t?.technicalTailGatePassed||sha(t.path)!==t.sha256||t.sampleRate!==24000)throw Error('Current PCM mismatch '+id);
 const role=explanation.has(id)?'explanation':s.role,ranges=role==='explanation'?[]:(changes[id]||s.ranges);
 const source=role==='explanation'?null:(s.sourcePath?{path:s.sourcePath,sha256:s.sourceSha256||sha(s.sourcePath)}:sources[s.source]);
 if(role==='actual'&&!source)throw Error('Source missing '+id);
 const cuts=ranges.map(([a,z])=>({inFrame:Math.ceil(a*60-1e-5),outFrame:Math.floor(z*60+1e-5),nativeSeconds:[a,z]}));
 for(const cut of cuts){
  const prior=intervals.get(source.path)||[];for(const p of prior)if(Math.max(p.inFrame,cut.inFrame)<Math.min(p.outFrame,cut.outFrame))throw Error('Repeated proposed source '+p.id+' / '+id);
  prior.push({...cut,id});intervals.set(source.path,prior);
 }
 const pcmFrames=Math.ceil(t.samples/400),capacityFrames=cuts.reduce((n,x)=>n+x.outFrame-x.inFrame,0);
 rows.push({id,effectiveRole:role,insertAfter:id==='appearance-to-controls'?'hogwarts-courtyard-ui':s.insertAfter,source,proposedCuts:cuts,pcm:{path:t.path,sha256:t.sha256,samples:t.samples,sampleRate:t.sampleRate},pcmFrames,capacityFrames,shortfallFrames:role==='actual'?Math.max(0,pcmFrames-capacityFrames):0,ko:s.ko,en:s.en,fullSourceMotionApproved:false,movingAnnotationApproved:false,finalNativeFrames:null});
}
if(rows.length!==46)throw Error('Expected46 current additions');
const p=read(b+'measured-additive-physical-split-v39.json').parts.find(x=>x.physicalPart===3),fr=read(b+'physical-framing-selected-execution-v55.json').results.find(x=>x.id==='part3-overview');
const E=p.preservedExplanationFrames+Math.ceil(fr.samples/400)+rows.filter(x=>x.effectiveRole==='explanation').reduce((n,x)=>n+x.pcmFrames,0),needed=Math.round(E*1.5)-p.preservedActualFrames,capacity=rows.filter(x=>x.effectiveRole==='actual').reduce((n,x)=>n+x.capacityFrames,0);
const bindings=[b+'native-followup-asr-direct-review-v130.json',b+'native-onset-asr-direct-review-v133.json',b+'aligned-native-source-review-v119.json',b+'native-source-followup-review-v127.json',b+'focus-analysis-classification-v96.json'].map(ref);
const value={schemaVersion:1,preparedAt:new Date().toISOString(),status:'current-takes-and-disjoint-native-capacity; continuous review required',bindings,rows,part3:{preservedActualFrames:p.preservedActualFrames,preservedExplanationFrames:p.preservedExplanationFrames,overviewFrames:Math.ceil(fr.samples/400),explanationFrames:E,neededNewActualFrames:needed,candidateCapacityFrames:capacity,surplusCandidateFrames:capacity-needed,exactRatioAllocationApproved:false},limits:['Proposed exposure extensions and four complete game cuts require direct full-speed read before selection. No card/idle quota.','Every chosen active cut and narration onset must be reviewed together; native capacity does not approve final timing or actual60:explanation40.','Original111 PCM, existing native allocations, chapter model renders and old take history preserved.'],newGitImages:0,sourceAudio:0,loop:0,slowdown:0,allFinalPixelsReviewed:false,finalMixedAsrApproved:false,collected:false,uploaded:false};
fs.writeFileSync(path.join(root,out),JSON.stringify(value,null,2)+'\n');
const htmlPath='production/research/game-lighting-history/local/selected-part3-native-review-v134.html';
if(fs.existsSync(path.join(root,htmlPath)))throw Error('Preserve previous player');
let html=fs.readFileSync(path.join(root,'production/research/game-lighting-history/local/followup-native-review-v123.html'),'utf8'),start=html.indexOf('<script>const rows='),end=html.indexOf(';const pick=',start);
const playerRows=rows.filter(x=>x.effectiveRole==='actual').map(x=>({id:x.id,path:x.source.path,sha256:x.source.sha256,ranges:x.proposedCuts.map(c=>[c.inFrame/60,c.outFrame/60]),ko:x.ko}));
html=html.slice(0,start)+'<script>const rows='+JSON.stringify(playerRows).replaceAll('<','\\u003c')+html.slice(end);fs.writeFileSync(path.join(root,htmlPath),html);
console.log(JSON.stringify({out,rows:rows.length,actualRows:playerRows.length,part3:value.part3,shortfalls:rows.filter(x=>x.shortfallFrames).map(x=>({id:x.id,missingSeconds:x.shortfallFrames/60})),allFinalPixelsReviewed:false}));
