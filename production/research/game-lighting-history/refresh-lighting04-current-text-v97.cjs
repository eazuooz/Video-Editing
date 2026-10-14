// A bounded direct reread of the four changed foreign scripts; no foreign edits.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const expected={
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.ko.json':'5d4ffd49100f8d1f2e69c20c6370ead654864ecd84afac8db0c8d758dbe00514',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.en.json':'c1bd04f36cdf515cf21f1deccd0506b60745b4a91ae9aa4022ed81f2b6c0f60d',
 'projects/game-math-quaternion-foundations-v3/script/narration.ko.json':'e3a8dda51476e837e9ffc59b51b7e0588377747b8bba652155db04e1200af1ac',
 'projects/game-math-quaternion-foundations-v3/script/narration.en.json':'0f2cd73672bcf3246eb04268b3deb3ebce7d66d7cc5ea2d09aac16d922bdc84b'
};
const previous=read('production/preflight/game-lighting-history-04.json');
for(const x of previous.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Another input needs direct review '+x.path);
for(const [p,h] of Object.entries(expected))if(sha(p)!==h)throw Error('Reviewed script changed '+p);
const cross=[],foundations=[];
for(const lang of ['ko','en']){
 const p='projects/game-math-quaternion-cross-game-additions-v3/script/narration.'+lang+'.json',x=read(p);
 if(x.scenes.length!==14)throw Error('Unexpected cross-game scope');
 cross.push({path:p,sha256:sha(p),completeCurrentScriptDirectlyRead:true,metadata:{project:x.project,language:x.language,status:x.status},scenes:x.scenes});
 const q='projects/game-math-quaternion-foundations-v3/script/narration.'+lang+'.json',y=read(q),b='projects/game-math-quaternion-foundations-v2/script/narration.'+lang+'.json',z=read(b);
 if(z.scenes.length!==43||!z.scenes.every(s=>y.scenes.some(t=>JSON.stringify(t)===JSON.stringify(s))))throw Error('Original foundation dictionaries changed');
 const added=y.scenes.filter(s=>!z.scenes.some(t=>t.id===s.id));if(added.length!==7)throw Error('Unexpected additions');
 foundations.push({path:q,sha256:sha(q),baseline:{path:b,sha256:sha(b)},original43SceneDictionariesExactlyEqual:true,completeSevenCurrentAddedScenesDirectlyRead:true,metadata:{project:y.project,language:y.language,status:y.status},addedScenes:added});
}
const output='production/research/game-lighting-history/episode04-current-text-rereview-v97.json';
if(fs.existsSync(output))throw Error('Preserve the prior audit');
const reason='Directly reread all14 paired quaternion cross-game scenes and all7 paired foundation insertions, including shortened gameplay guides. Original43 foundation scene dictionaries exactly match the already reviewed v2 baseline. Aircraft nose/wing directions, component orientation versus standing upright, selected Besiege parts, same-axis inverse, ordered rotations and length preservation remain orientation mathematics, distinct from rendering-history lighting/reconstruction/exposure/resource/frame-input-output teaching. No other inventory file changed; carry actual Studio review v68 and full inventory/content review v91. Preserve all foreign scripts and current uploads. Evidence: '+output;
fs.writeFileSync(output,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:'production/research/game-lighting-history/episode04-current-wording-rereview-v91.json',crossGamePairedReview:cross,foundationEquivalence:foundations,contentComparison:reason,decision:'distinct',actualStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',foreignFilesModified:false,currentRenderingRatioApproved:false,allFinalPixelsReviewed:false,uploaded:false,newGitImages:0},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',output],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
