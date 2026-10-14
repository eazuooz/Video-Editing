// Only the two complete outlines directly reread in this checkpoint may differ.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const expected={
 'projects/game-math-quaternion-calculations-v3/planning/outline.md':'d01077a74d3a0def32426c680ed15975ba85ae9d57f1b240d2621c2515d83a0d',
 'projects/game-math-quaternion-foundations-v3/planning/outline.md':'e1bfbece0635e216a04d05fc5ea4e2b0dc3b707d1c26a96b5a2a123308c2feb1'
};
const prev=read('production/preflight/game-lighting-history-04.json');
for(const x of prev.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Another input requires direct reread '+x.path);
const out='production/research/game-lighting-history/episode04-outline-delta-review-v115.json';if(fs.existsSync(out))throw Error('Preserve existing evidence');
const reason='Directly reread both complete current quaternion calculation/foundation outlines. They preserve orientation formulas/PCM and teach nose/wing, object versus camera direction, same-axis inverse, selected Besiege part orientation and vector results across Riders Republic, Trailmakers, Space Engineers and Besiege. These are orientation operations rather than lighting, visibility, reconstruction, exposure or frame-resource inspection. Besiege external-upload source attribution remains pending in the foreign outlines. Retain their40:60/noBGM/white exceptions only in those productions. Scripts and other inventory inputs are byte-identical to the preceding direct full review v97; actual Studio evidence v68 and full inventory review v91 carried forward. No foreign file edited. Evidence: '+out;
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:'production/research/game-lighting-history/episode04-current-text-rereview-v97.json',completeOutlineReads:Object.entries(expected).map(([path,sha256])=>({path,sha256,fullBodyDirectlyRead:true,text:fs.readFileSync(path,'utf8')})),decision:'distinct',reason,foreignFilesModified:false,allFinalPixelsReviewed:false,uploaded:false,newGitImages:0},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
