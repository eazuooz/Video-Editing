const fs=require('node:fs'),crypto=require('node:crypto'),cp=require('node:child_process');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const expected={
 'projects/game-math-quaternion-calculations-v3/project.json':'4e26fc54230482b93c04e36f8b305f9998d68d0af3a1d636736ae7d82aae2d1f',
 'projects/game-math-quaternion-foundations-v3/project.json':'05c8f0f0757c3bc9fe9ebed982b3e3344ee203e07d77d35abd5d7f34fa47e8d1'
};
const prev=read('production/preflight/game-lighting-history-04.json');
for(const x of prev.inputFiles)if(sha(x.path)!==(expected[x.path]||x.sha256))throw Error('Unreviewed change '+x.path);
const out='production/research/game-lighting-history/episode04-manifest-delta-review-v122.json';
if(fs.existsSync(out))throw Error('Preserve existing review');
const reason='Directly reread both complete changed quaternion v3 manifests, including complete bilingual description/chapter preparation, original PCM preservation, white/noBGM lecture exception, exact40:60 figures, and two-scene source-overlay refinement paths. Their viewer questions and Hamilton/vector/inverse/composition convention remain distinct from rendering inputs, lighting and reconstruction. Full narration/outlines/source notes and other v118 inventory inputs remain byte-identical. Prepared metadata remains prepared; no new actual Studio action or completed upload is inferred. Carry forward actual Studio v68. Evidence: '+out;
const requestPath='projects/game-lighting-history-04/production/native-followup-request-v120.json',before={path:requestPath,sha256:sha(requestPath)};
fs.writeFileSync(out,JSON.stringify({schemaVersion:1,reviewedAt:new Date().toISOString(),previousReview:'production/research/game-lighting-history/episode04-current-delta-review-v118.json',completeChangedFiles:Object.entries(expected).map(([path,sha256])=>({path,sha256,fullBodyDirectlyRead:true})),fullNarrationScriptsChanged:false,decision:'distinct',reason,sourceStudioEvidence:'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json',preModelStop:{sessionId:59404,exitCode:1,executionStateCreated:false,narrationFilesCreated:false,researchRestoration:'shared/output/gpu-handoff/4652b727-c091-42cb-b593-16c89e7b8d1e.json',researchQueuePid:84536,state:'research_resume_verified',cause:'Concurrent foreign manifest change invalidated duplicate review before model import.'},originalPreparedRequest:before,foreignFilesModified:false,uploaded:false},null,2)+'\n');
const args=['scripts/review-video-duplicates.cjs','game-lighting-history-04','--candidate-file','production/research/game-lighting-history/candidate-04.json'];
cp.execFileSync(process.execPath,[...args,'--decision','distinct','--reason',reason,'--studio-evidence',out],{stdio:'inherit'});
cp.execFileSync(process.execPath,[...args,'--check'],{stdio:'inherit'});
const r=read(requestPath);r.previousCurrentDuplicateReview=r.currentDuplicateReview;r.currentDuplicateReview={path:out,sha256:sha(out)};r.preModelStopEvidence=out;
fs.writeFileSync(requestPath,JSON.stringify(r,null,2)+'\n');
