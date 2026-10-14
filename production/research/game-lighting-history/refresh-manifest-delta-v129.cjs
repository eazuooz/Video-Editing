const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const expected={
 'projects/game-math-quaternion-calculations-v3/project.json':'f9d476a28b049f2b9395bd89994841e06ce951f8aa32419acac389094e19981f',
 'projects/game-math-quaternion-foundations-v3/project.json':'bfc914fb6fde45b3a2627be3a3fcb020b786ad0e4dabcdff03e02b3c61e268f4'
};
const prev=read('production/preflight/game-lighting-history-04.json');
for(const x of prev.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Unreviewed change '+x.path);
const out='production/research/game-lighting-history/episode04-manifest-delta-review-v129.json';
if(fs.existsSync(out))throw Error('Preserve existing review');
const reason='Directly reread both complete changed quaternion v3 manifests. New refined-v2 master paths, narration-timed source-overlay refinements, orbit interval hide and caption-clearance adjustments change their prepared render inputs; original eighty scenes and narration are preserved, and actual upload remains false. Their Hamilton/right-handed/wxyz rotation, inverse and composition questions remain distinct from lighting, reconstruction and selected graphics-command outputs. Their full scripts, outlines, sources and all other current preflight inputs remain byte-identical to the prior direct review. No new Studio result inferred; carry actual Studio v68. Evidence: '+out;
const requestPath='projects/game-lighting-history-04/production/native-onset-request-v128.json';
if(fs.existsSync('projects/game-lighting-history-04/production/native-onset-execution-v128.json'))throw Error('Do not mutate an executed request');
const originalRequest={path:requestPath,sha256:sha(requestPath)};
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:'production/research/game-lighting-history/episode04-manifest-delta-review-v122.json',completeChangedFiles:Object.entries(expected).map(([path,sha256])=>({path,sha256,fullBodyDirectlyRead:true})),fullNarrationScriptsChanged:false,decision:'distinct',reason,sourceStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',preflightStop:{dryRun:true,exitCode:1,executionStateCreated:false,newNarrationCreated:false,gpuLeaseAcquired:false,cause:'Concurrent foreign manifest changes invalidated the current duplicate review.'},originalRequest,foreignFilesModified:false,uploaded:false},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
const r=read(requestPath);r.previousCurrentDuplicateReview=r.currentDuplicateReview;r.currentDuplicateReview={path:out,sha256:sha(out)};
fs.writeFileSync(requestPath,JSON.stringify(r,null,2)+'\n');
