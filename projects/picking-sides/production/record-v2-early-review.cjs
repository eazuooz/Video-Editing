const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const base='projects/picking-sides/production/',voice='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2/';
const evidence=read(voice+'picking-sides-qwen3-1.7b-balanced-v2.asr-review.json');
const decisions={
 '01':{decision:'content-readback-pass',reason:'All seven paragraphs match normalized original wording. Distinct trailer cuts and early developer footage caveats are retained; no added greeting, omission, or repetition.'},
 '02':{decision:'rejected-missing-bridge-prefix',reason:'All four unchanged explanation paragraphs recovered. The new bridge omits 지금부터 in the full scene, isolated bridge, and composite-tail read-backs. Preserve original29.175seconds PCM; repair only the new bridge. Ending heuristic pass is not sufficient.'},
 '03':{decision:'content-readback-pass',reason:'All seven paragraphs recovered, including identity clues, edge grip, and not-a-controlled-experiment caveat. ASR 정해→정에 is a minor phonetic ambiguity; no claim missing or repeated. Human listening remains pending.'},
};
const reviewed=Object.entries(decisions).map(([id,d])=>{
 const found=evidence.scenes.find(s=>s.scene===id),wav=voice+'chunks/'+id+'-scene.wav';
 if(!found||found.audio_sha256!==hash(wav))throw Error('Stale review '+id);
 return {id,...d,audioSha256:found.audio_sha256,wav,approvedAsr:voice+'asr/'+id+'.json',
 acousticChecks:found.acousticChecks,expected:found.expected,recognized:found.recognized};
});
write(base+'existing-game-replan/early-asr-direct-review.json',{reviewedAt:new Date().toISOString(),
 directTextComparison:true,reviewedParagraphs:19,scenes:reviewed,
 boundaryProof:base+'existing-game-replan/boundary02/asr.json',humanListening:'pending',allCurrentScenesTechnicallyReviewed:false});
const approval=read(base+'voice-approval.json');
for(const s of reviewed.filter(s=>s.decision==='content-readback-pass')){
 approval.scenes=approval.scenes.filter(x=>x.id!==s.id);approval.scenes.push(s);
}
approval.scenes.sort((a,b)=>a.id.localeCompare(b.id));approval.reviewedAt=new Date().toISOString();
approval.allCurrentScenesTechnicallyReviewed=false;
approval.pendingScene02=reviewed.find(s=>s.id==='02');write(base+'voice-approval.json',approval);
const boundary=read(base+'existing-game-replan/boundary02/asr.json');
boundary.directReview='confirmed-bridge-prefix-omission; candidate repair queued; no composite replacement';
write(base+'existing-game-replan/boundary02/asr.json',boundary);
write(base+'existing-game-replan/reserve03/review.json',{
 reviewedAt:new Date().toISOString(),sourceId:'Z5jytMiH4rI',reason:'Measured03first two paragraphs need20.18seconds; current approved game range70–85only15seconds.',
 contactSheets:['Z5jytMiH4rI-84-116-2-contact-1.png','Z5jytMiH4rI-84-116-2-contact-2.png'],
 directlyInspectedAdditionalCropTimes:[85.1,87.6,90.25,90.5,68.8,69.2,69.6,89.2],
 candidate:{start:85,end:90.4,normalSpeed:true,sourceAction:'Same robot monkey and hat bunny continue jumping between rooftop positions; no menu through these samples.',
 needsFinalCompositionReview:true,finalApproved:false,
 concerns:['Source black top margin changes during zoom; crop y64/y84 still leaves a narrow black line in later samples.','Bunny descends toward bottom caption area near90seconds. Need final temporal crop/cue review or a different additional real-play range.']},
 excluded:[{start:68.8,end:69.6,reason:'Treehouse character selection/menu, not actual play quota'},{start:92,end:98,reason:'Party voting/loading screens'},{start:100,end:114,reason:'Different tiny underground action does not reliably illustrate the currently spoken costume comparison'}],
 frozenActionMapUnchanged:true,finalCueReview:false
});
console.log('Saved direct19paragraph review; two actual scenes pass, scene02bridge repair queued, scene03source fit requires final expansion.');
