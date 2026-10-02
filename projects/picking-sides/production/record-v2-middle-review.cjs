const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),base='projects/picking-sides/production/';
const voice='shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,v)=>fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const report=read(voice+'picking-sides-qwen3-1.7b-balanced-v2.asr-review.json');
const reviewed=['05','07'].map(id=>{
 const r=report.scenes.find(s=>s.scene===id);if(!r||r.audio_sha256!==hash(voice+'chunks/'+id+'-scene.wav'))throw Error('Stale ASR '+id);
 return {...r,decision:'not-approved-pronunciation-repair-required',
 reason:id==='05'?'Full ASR adds 바스킹 before the game name; independent first12seconds read-back gives 가스캥. All other seven-paragraph claims are present, but do not approve the spoken game-name prefix.':'Both full and independent middle excerpts read 닭의 점프 as 달걀/달개 점프 twice. Rephrase those two new actual-footage sentences for clear chicken identification; retain all six original explanation chapters.',
 humanListening:'pending'};
});
write(base+'existing-game-replan/middle-asr-direct-review.json',{reviewedAt:new Date().toISOString(),
 directTextComparison:true,paragraphs:14,scenes:reviewed,allCurrentScenesTechnicallyReviewed:false,
 independentEvidence:base+'existing-game-replan/uncertain-words/asr.json',
 frozenInputsUnchanged:true,nextAction:'Wait for current parent and bridge-candidate repair before modifying frozen text. Repair only affected new actual-game narration; update KO/EN and current-hash ASR before measured editing.'});
const a=read(base+'voice-approval.json');a.allCurrentScenesTechnicallyReviewed=false;
a.pendingActualScenes=reviewed;write(base+'voice-approval.json',a);
const u=read(base+'existing-game-replan/uncertain-words/asr.json');
u.directReview='Game-name prefix and chicken-possessive ambiguity reproduced; keep05/07unapproved pending repair';write(base+'existing-game-replan/uncertain-words/asr.json',u);
write(base+'existing-game-replan/source-timing-followup.json',{
 reviewedAt:new Date().toISOString(),frozenActionMapUnchanged:true,finalEditApproved:false,
 measuredSpeechSourceFit:base+'existing-game-replan/provisional-speech-source-fit.json',
 scene03:{
   originalGroupShortfallSeconds:5.18,
   proposedSolution:'Extend UCH70–85 with fresh85–86.5667 using crop120,100,1664,936. Cut to truck gameplay at scene-local16.5667 as the general sentence 화면 속 위치만 기억하면 begins, not during the animal-specific claim. Game-name introduction follows at20.18. No loop, speed change, or narration cut.',
   observedWordBoundary:16.56,sourceSample:base+'existing-game-replan/reserve03/86.5-safe.png',
   rationale:'The preceding sentence about the same animal ends16.30. The following general positional-memory limitation also applies to the truck shot. Both costume characters remain above the fixed caption area at86.5.',
   finalCueAndTransitionReview:'pending',rejectedExtension:'Do not extend to90.4without correction: changing black borders and falling bunny enter caption area.'
 },
 scene07:{
   measuredTruckGroupMinimumSeconds:23.96,bankSeconds:19,
   freshRoofCandidate:{sourceId:'iagyci5LMTY',start:664,end:674,sourceAudio:'muted',speed:1,loop:false,
     action:'Cyan, yellow and green bodies grapple and change position on the near truck roof while the camera rotates; meaningful continuation of the different attempt already shown at651–664.',
     evidence:base+'official-source-review/iagyci5LMTY-650-683-3-contact-1.png',
     selectedForFinal:false},
   remainingIssue:'Match the initial hanging-body paragraph to an adequately long, unobscured hand/edge interval; additional roof footage covers only later roof/grip/camera commentary. Re-measure after pronunciation repair.',
   excluded:{sourceId:'iagyci5LMTY',start:617,end:635,reason:'Bodies largely obscured behind trucks; not adequate hand/edge evidence.',
     evidence:base+'official-source-review/iagyci5LMTY-617-650-3-contact-1.png'}
 },
 gondolaReserves:{sourceId:'VOZRzwlzQeA',reviewedContactInterval:[49,89],
   evidence:[base+'official-source-review/VOZRzwlzQeA-49-89-3-contact-1.png',base+'official-source-review/VOZRzwlzQeA-49-89-3-contact-2.png'],
   candidateIntervals:[[66,70.6],[72.5,83.2]],reason:'Fresh red/yellow gripping and platform-edge action. Preserve cuts between distinct attempts, never imply continuity across resets.',
   finalCueReview:'pending',selectedForFinal:false}
});
console.log('Saved14paragraph comparison, two pronunciation issues and measured source-fit remedies; final approval remains false.');
