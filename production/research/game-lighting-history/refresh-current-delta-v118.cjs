const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p,'utf8')).digest('hex');
const expected={
 'projects/game-math-polygons-triangulation/publishing/youtube-upload.json':'8bffdbf84397ba30cd8587403fea1df38f7081908aeae802da98d78d0a7786a8',
 'projects/game-math-quaternion-calculations-v3/project.json':'1f366399c2e94da27a53bb01f732413e70252f544e5804ef1b2694d7133de12c',
 'projects/game-math-quaternion-calculations-v3/planning/outline.md':'a9931655cbab73c34eaa7db4609e62db70ef65c3275a29d91edeb470ab1d7c51',
 'projects/game-math-quaternion-calculations-v3/sources/SOURCES.md':'a7e8f6a124f8f4115ac61c42045d1319aa7feaf99b1ef68354f7780f671dec83',
 'projects/game-math-quaternion-foundations-v3/project.json':'7a6296883f16b259a34ce55c40e48e99d8adbdd980685a30a122ad108c6fcd92',
 'projects/game-math-quaternion-foundations-v3/planning/outline.md':'1c6f313de9de671a298888f5ea11afd56ad02734a32bf46af8fcf275c703f346',
 'projects/game-math-quaternion-foundations-v3/sources/SOURCES.md':'a7e8f6a124f8f4115ac61c42045d1319aa7feaf99b1ef68354f7780f671dec83'
};
const prev=read('production/preflight/game-lighting-history-04.json');
for(const x of prev.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Unreviewed delta '+x.path);
const out='production/research/game-lighting-history/episode04-current-delta-review-v118.json';
if(fs.existsSync(out))throw Error('Preserve earlier direct review');
const reason='Directly reread seven changed complete files: both quaternion v3 manifests/outlines/source notes, and the polygon upload receipt including full KO/EN metadata and replacement/deletion history. Quaternion operations remain storage/half-angle, sign, inverse, composition, relative target rotation and vector rotation across four games. Besiege required-link permission is specific to the foreign lecture. Polygon receipt describes triangle centers, convexity and ear clipping; its saved history now records replacement IDs YgcN8vs0gNo/pfagaQK-xfI and action-time confirmed deletion of L7SXFwn4i2k. These subjects remain distinct from rendering, lighting/reconstruction and frame-resource inspection. All full narration scripts and other prior inventory inputs are byte-identical to directly read v97/v91 evidence. Carry forward actual Studio review v68; do not claim a new Studio action here. Foreign40:60/noBGM/white exceptions stay foreign. Evidence: '+out;
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:'production/research/game-lighting-history/episode04-outline-delta-review-v115.json',completeChangedFiles:Object.entries(expected).map(([path,sha256])=>({path,sha256,fullBodyDirectlyRead:true})),fullNarrationScriptsChanged:false,actualStudioEvidenceCarriedForward:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',decision:'distinct',reason,foreignFilesModified:false,uploaded:false,newGitImages:0},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
