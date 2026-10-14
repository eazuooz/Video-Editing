// New foreign quaternion additions were directly read; foreign files stay intact.
const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const previous=read('production/preflight/game-lighting-history-04.json');
for(const x of previous.inputFiles)if(!fs.existsSync(x.path)||sha(x.path)!==x.sha256)throw Error('Another changed prior input needs review '+x.path);
const names=['game-math-quaternion-foundations-v3','game-math-quaternion-calculations-v3','game-math-quaternion-cross-game-additions-v3'];
const expected={
 'projects/game-math-quaternion-calculations-v3/project.json':'6046b42e29cc6c3cc968e6e8d39daeb65d6a04ff7c07cd3a1f81bae44c41f971',
 'projects/game-math-quaternion-calculations-v3/script/narration.ko.json':'c91c55f9e5444f0a58d61cafae0f8b2e7607f875730266c2e6baa8303dd73af5',
 'projects/game-math-quaternion-calculations-v3/script/narration.en.json':'882f143feac6f92dd8afa1418cfa5871f774dd48059610545ff4efe12f4f3c0c',
 'projects/game-math-quaternion-calculations-v3/planning/outline.md':'8d6c6d63036b9e2297083325d58bb07c0fe5b85d31672a379e6f1ab4ba95633c',
 'projects/game-math-quaternion-calculations-v3/sources/SOURCES.md':'fd85a117148d4331a5f360cc12293510214e48fc06c852b627e7fbbbc3ec739e',
 'projects/game-math-quaternion-cross-game-additions-v3/project.json':'c380a46a4b1523fb70a4e0e0c2b1f611bea7b95cfab4cb1303ac5ae3d0446f3d',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.ko.json':'5f8a427034d60d334e8ab78fb374eda5883c7e719f3afdf34b22ae51df8fa54e',
 'projects/game-math-quaternion-cross-game-additions-v3/script/narration.en.json':'b78c689cec5ccc26597bd7fe8aed7156d74e411d2ccd2b4f870974bdce4167f7',
 'projects/game-math-quaternion-foundations-v3/project.json':'15da05e08d03779a884c6b50169946d616f12b24573719471543c156fbd6f8a3',
 'projects/game-math-quaternion-foundations-v3/script/narration.ko.json':'f34c692e1812f9737fd432be7906e6b2a265363f7df143d9fa69dacbc048c4dd',
 'projects/game-math-quaternion-foundations-v3/script/narration.en.json':'a10d57edf6057d140104de5368e32d983fbd13c17a60e48caaddc1fe799f6836',
 'projects/game-math-quaternion-foundations-v3/planning/outline.md':'9959b3d8ae5f36d11931d979b220aac2751e57b4d1176af4eb98d7350a1821dd',
 'projects/game-math-quaternion-foundations-v3/sources/SOURCES.md':'fd85a117148d4331a5f360cc12293510214e48fc06c852b627e7fbbbc3ec739e'
};
for(const [p,h] of Object.entries(expected))if(sha(p)!==h)throw Error('New foreign delta changed '+p);
const equivalence=[];
for(const name of names.slice(0,2))for(const lang of ['ko','en']){
 const manifest=read('projects/'+name+'/project.json'),baseline='projects/'+manifest.revisionOf+'/script/narration.'+lang+'.json',current='projects/'+name+'/script/narration.'+lang+'.json';
 if(!previous.inputFiles.some(x=>x.path===baseline&&x.sha256===sha(baseline)))throw Error('Prior full-script baseline not bound');
 const a=read(baseline),b=read(current),map=new Map(a.scenes.map(x=>[x.id,x]));
 if(a.scenes.some(x=>!b.scenes.some(y=>y.id===x.id&&JSON.stringify(y.lines)===JSON.stringify(x.lines))))throw Error('Original scene wording changed');
 const additions=b.scenes.filter(x=>!map.has(x.id));if(additions.length!==7)throw Error('Inspect changed addition scope');
 equivalence.push({current,baseline,baselineSha256:sha(baseline),baselineCompleteReviewCarried:true,allBaselineSceneLinesExactlyEqual:true,currentScenes:b.scenes.length,currentParagraphs:b.scenes.reduce((n,x)=>n+x.lines.length,0),addedCompleteParagraphsDirectlyRead:true,addedScenes:additions.map(x=>({id:x.id,title:x.title,lines:x.lines})),currentFullScriptNewlyReread:false});
}
const out='production/research/game-lighting-history/episode04-current-quaternion-rereview-v86.json';if(fs.existsSync(out))throw Error('Preserve prior review');
const reason='The three new quaternion manifests and both outlines/source records were directly read. Complete KO/EN fourteen-scene cross-game addition scripts and all seven inserted scenes in each foundation/calculation script were directly compared. Their old43/37-scene wording is exactly equal to the previously fully reviewed v2 scripts, whose current hashes remain in the prior83-project snapshot. Foundations adds aircraft axes, the half-angle representation, same rotation preserving a right angle and cancelling a rotation; calculations adds noncommutative order, D=B*inverse(A), and q*v*inverse(q) with length preservation. Riders Republic, Trailmakers, Space Engineers and Besiege illustrate orientation, not renderer inputs/display controls. This differs from our chronological rendering/reconstruction and captured resource pipeline. Their pending Besiege credits/rights, white40:60/noBGM contracts, old IDs HdJw7bgKlbM/SPq_41LyOG0 and schedules remain untouched. No new upload receipt exists. Carry unchanged prior83 full-script and actual Studio evidence v68/v77; now86 projects. Own original111/current37/five framing inputs remain intact, and coverage/ratio/final mix/moving pixels/private approvals stay false. Evidence: '+out;
fs.writeFileSync(out,JSON.stringify({reviewedAt:new Date().toISOString(),previous:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v77.json',newFiles:Object.entries(expected).map(([path,sha256])=>({path,sha256})),completeNewManifestsDirectlyRead:true,newPairedAdditionScriptsDirectlyRead:true,baselineEquivalence:equivalence,comparison:reason,decision:'distinct',actualStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',foreignFilesModified:false,newGitImages:0},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
