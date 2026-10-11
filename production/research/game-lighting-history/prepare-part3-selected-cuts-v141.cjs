const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const ref=p=>({path:p,sha256:sha(p)});
function write(p,s){const abs=path.join(root,p);if(fs.existsSync(abs))throw Error('Preserve prior '+p);fs.writeFileSync(abs,typeof s==='string'?s:JSON.stringify(s,null,2)+'\n');}
const prior=b+'selected-part3-source-plan-v134.json',p=read(prior);
const fix={
 'exposure-context':[[1567.6,1572.1],[1577.7,1586],[1621,1626.6]],
 'hogwarts-stair-reference':[[0,1000/60]],
 'hogwarts-arch-camera':[[18,18+1280/60]],
 'hogwarts-terrace-reference':[[43,43+1180/60]],
 'hogwarts-brazier-view':[[65,65+1060/60]],
 'hogwarts-hall-camera':[[120,120+1395/60]],
 'hogwarts-courtyard-ui':[[160,160+950/60]]
};
const insertion={'appearance-to-controls':'original-22-5','focus-legend-context':'focus-layers-entry','focus-to-frame-inspection':'original-22p-6'};
for(const r of p.rows){
 if(fix[r.id]){r.proposedCuts=fix[r.id].map(([a,z])=>({inFrame:Math.round(a*60),outFrame:Math.round(z*60),nativeSeconds:[a,z]}));r.capacityFrames=r.proposedCuts.reduce((n,c)=>n+c.outFrame-c.inFrame,0);r.shortfallFrames=Math.max(0,r.pcmFrames-r.capacityFrames);}
 if(insertion[r.id])r.insertAfter=insertion[r.id];
 if(r.id==='exposure-context')r.onScreenConditionLabel='같은 시연의 별도 구간 · 카메라/설정 조건 변화';
 if(r.id==='focus-normal-return')r.onScreenConditionLabel='뒤의 일반 화면 · 다른 설정/카메라';
 if(r.id==='focus-error-isolation')r.onScreenConditionLabel='앞선 진단 화면 · 별도 조건';
}
const intervals=new Map();for(const r of p.rows.filter(r=>r.effectiveRole==='actual')){if(sha(r.source.path)!==r.source.sha256||sha(r.pcm.path)!==r.pcm.sha256||r.shortfallFrames)throw Error('Source/full PCM capacity '+r.id);const list=intervals.get(r.source.path)||[];for(const c of r.proposedCuts){for(const old of list)if(Math.max(c.inFrame,old.inFrame)<Math.min(c.outFrame,old.outFrame))throw Error('Repeated new cuts '+r.id+'/'+old.id);list.push({...c,id:r.id});}intervals.set(r.source.path,list);}
p.prior=ref(prior);p.preparedAt=new Date().toISOString();p.status='Causal native onset and full-PCM allocation prepared; direct pixels still required';
p.originalPcmTailRepair={chapter:'inspection',preserveSamples:8013121,oldFrames:20032,currentFrames:20033,addedFrames:1,role:'explanation',placement:'Original conclusion final cut only',voiceRemovedSamples:0,newTts:0};
const E=p.part3.explanationFrames+1,A=p.part3.preservedActualFrames+p.rows.filter(r=>r.effectiveRole==='actual').reduce((n,r)=>n+r.capacityFrames,0);
p.part3={...p.part3,preservedExplanationFrames:p.part3.preservedExplanationFrames+1,explanationFrames:E,neededNewActualFrames:Math.round(E*1.5)-p.part3.preservedActualFrames,candidateCapacityFrames:A-p.part3.preservedActualFrames,surplusCandidateFrames:A-Math.round(E*1.5),actualFrames:A,bodyFrames:A+E,roundingErrorFrames:Math.abs(A-(A+E)*.6),exactRatioAllocationApproved:false};
if(p.part3.roundingErrorFrames>1)throw Error('Ratio allocation');
p.repairReason='PP controls appear at1577.7; shift the narration-aligned cut to controls at4.5 seconds, preserve the full18.4-second PCM and label discontinuous conditions. Preserve complete conceptual original ending before its bridge. Remove only useful-action tails after the preserved full narration; no loops or slowdown.';
write(b+'selected-part3-source-plan-v141.json',p);
const playerRows=p.rows.filter(r=>r.effectiveRole==='actual').map(r=>({id:r.id,path:r.source.path,sha256:r.source.sha256,ranges:r.proposedCuts.map(c=>[c.inFrame/60,c.outFrame/60]),ko:r.ko}));
let html=fs.readFileSync(path.join(root,'production/research/game-lighting-history/local/selected-part3-native-review-v134.html'),'utf8');const start=html.indexOf('<script>const rows='),end=html.indexOf(';const pick=',start);if(start<0||end<0)throw Error('Player marker');html=html.slice(0,start)+'<script>const rows='+JSON.stringify(playerRows).replaceAll('<','\\u003c')+html.slice(end);write('production/research/game-lighting-history/local/selected-part3-native-review-v141.html',html);
const qa=fs.readFileSync(path.join(root,'production/research/game-lighting-history/extract-guided-focus-qa-v139.py'),'utf8').replaceAll('v139','v143').replaceAll('V139','V143').replaceAll('v138','v142').replaceAll('all18','all6').replaceAll('all3','all1').replaceAll("len(layout['cues'])==18","len(layout['cues'])==6").replaceAll('frame<3280','frame<1100');write('production/research/game-lighting-history/extract-guided-focus-label-qa-v143.py',qa);
console.log(JSON.stringify({rows:p.rows.length,part3:p.part3,allFinalPixelsReviewed:false}));
