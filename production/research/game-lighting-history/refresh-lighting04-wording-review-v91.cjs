// Directly reviewed quaternion wording corrections; preserve foreign scripts.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const expected={
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.ko.json':'d6e86fc9a6db27de262950bde7283309115e2d1d42dce6fe22c595a1ecfde1f4',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.en.json':'072070985201e5f191541d0541bf1b3c001ac6be7024b8cd163a16a370f410df',
 'projects/game-math-quaternion-foundations-v3/script/narration.ko.json':'143de8500d2ed8b63fd25c57fb7f55c796c4fe1393d7bcad6550aed2e5b23c61',
 'projects/game-math-quaternion-foundations-v3/script/narration.en.json':'de63271ddb89e31a426be0961b7147c6202ba5e2c2e4c26fa5e30fa837d7ef5b'
};
const previous=read('production/preflight/game-lighting-history-04.json');
for(const x of previous.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Another input needs direct review '+x.path);
for(const [p,h] of Object.entries(expected))if(sha(p)!==h)throw Error('Reviewed wording changed '+p);
const baseline='production/research/game-lighting-history/episode04-current-quaternion-rereview-v86.json';
const oldReview=read(baseline),equivalence=[];
for(const lang of ['ko','en']){
 const current='projects/game-math-quaternion-foundations-v3/script/narration.'+lang+'.json';
 const old='projects/game-math-quaternion-foundations-v2/script/narration.'+lang+'.json';
 const a=read(old),b=read(current),review=oldReview.baselineEquivalence.find(x=>x.current===current);
 if(a.scenes.length!==43||!a.scenes.every(x=>b.scenes.some(y=>y.id===x.id&&JSON.stringify(y.lines)===JSON.stringify(x.lines))))throw Error('Original43 wording changed');
 const before=new Map(review.addedScenes.map(x=>[x.id,x]));
 const changed=b.scenes.filter(x=>before.has(x.id)&&JSON.stringify(x.lines)!==JSON.stringify(before.get(x.id).lines));
 if(changed.map(x=>x.id).join(',')!=='QF11,QF20,QF21')throw Error('Unexpected foundation delta');
 equivalence.push({current,baseline:old,baselineSha256:sha(old),original43SceneLinesExactlyEqual:true,unchangedFourAdditionsReviewCarried:true,completeChangedScenesDirectlyRead:changed.map(x=>({id:x.id,title:x.title,lines:x.lines})),currentFullScriptNewlyReread:false});
}
const output='production/research/game-lighting-history/episode04-current-wording-rereview-v91.json';
if(fs.existsSync(output))throw Error('Preserve existing review');
const reason='Directly reread both complete14-scene KO/EN quaternion cross-game scripts and paired QF11/QF20/QF21 foundation corrections. They replace an assumed right wing with a defined wing and distinguish standing a component upright from proving its full orientation restored; exact inverse rotation remains a checkable model. All original43 foundation scene lines and four other inserted scenes exactly match prior complete review. No other inventory inputs changed. These orientation/half-angle/inverse examples remain distinct from our rendering-history input/output, reconstruction, exposure, resource and frame-capture teaching. Carry current86-project content and Studio evidence v86/v77/v68 without changing any foreign project, receipt or schedule. Preserve original111, framing, all37 new takes; final coverage/ratio/mix/pixel/upload gates remain pending. Evidence: '+output;
fs.writeFileSync(output,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previous:baseline,changedFiles:Object.entries(expected).map(([path,sha256])=>({path,sha256})),completeCrossGamePairedScriptsDirectlyRead:true,foundationEquivalence:equivalence,contentComparison:reason,decision:'distinct',actualStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',foreignFilesModified:false,newGitImages:0},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',output],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
