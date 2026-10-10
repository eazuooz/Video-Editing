const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),p='projects/game-lighting-history-03/production/';
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8'));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const observations={
 'original-39':'Two projected probe planes appear on opposite sides of a wall; equal mixing shows E=6 despite the occluded bright probe. Visible faces and wall depth distinguish probe positions.',
 'original-40':'The right receiver changes from E=6 to E=2 while the left stays6; orange probe contribution is suppressed with wB1→0 and teal wA=1 remains.',
 'original-44':'Four labelled light candidates feed one reservoir; selected L2, M=4 and W=6 appear. This is a weighted-selection illustration, not a full lighting estimator.',
 'original-45':'Weights1 and3 build W=4; bins at u=.125/.375/.625/.875 show B,B,B,A and P=3/(1+3)=.75, preserving a nonzero chance for A.',
 'original-46':'Separate projected q/target-contribution/M blocks become linked by role-colored arrows; selection probability is explicitly distinguished from a completed lighting estimate.',
 'original-47':'Neighbor and previous-frame planes send separate orange/green arrows into the current sample. Text requires normal, position and visibility rechecks.',
 'original-48':'The projected door actually rotates closed; a previously visible candidate becomes occluded. The final visible state says current visibility is blocked.',
 'original-52':'The 4×4 projected depth grid retains eight teal samples and crosses eight occluded samples; .3 front depth versus .8 behind depth is separate from a GPU speed claim.',
 'original-53':'The left4×4 depth plane becomes accompanied by a right2×2 maximum-depth summary .3/.4/.5/.8. Near0/far1 and reversed-depth comparison caveats remain visible.',
 'original-54':'A door panel moves aside, revealing a new object while the red old-depth panel remains; current visibility differs from the previous occlusion record.',
 'original-56':'Four projected mesh groups show the fourth group fading as visibility reduces work; the text distinguishes geometry processing from indirect lighting.',
 'original-57':'The output grid remains16 pixels while orange16 evaluation points become teal4; geometry and output resolution do not change with shading frequency.',
 'original-58':'One evaluation sends teal arrows to a projected2×2 block. The on-screen limit explicitly rejects an unconditional4× whole-frame speedup.',
 'original-59':'An8×8 virtual page plane highlights five requested pages and a separate resident plane reveals IDs9,10,17,18,27. Page management is not learned texture generation.',
 'original-60':'Four orange requested pages stay on the left while the right arrival count progresses from0 to4; demand feedback does not mean instantaneous residency.',
 'original-65':'With f=1000px and world error=.01m, distance changes2→4m and projected error5→2.5px; the orange object shrinks spatially. This approximation is not Nanite’s complete selection rule.',
 'original-81-explanation':'Four projected cache blocks progressively turn orange, with the active update label1→4; four blocks are an independent explanation, not a measured Lumen update budget.'
};
const planPath=p+'caption-clearance-repair-plan-v3.json',plan=read(planPath),executionPath=p+'explanation-clearance-inputs-execution-v19.json',execution=read(executionPath);
if(execution.status!=='complete'||plan.clips.length!==17||Object.keys(observations).length!==17)throw Error('Incomplete actual input review');
const clips=plan.clips.map(c=>{const output='production/research/game-lighting-history/local/explanation-clearance-inputs-v19/'+c.id+'.mp4';const v=read(output.replace(/\.mp4$/,'.verification.json'));if(sha(output)!==v.outputSha256||v.observedFrames!==c.frames)throw Error('Changed reviewed input '+c.id);return {id:c.id,fromFrame:c.fromFrame,toFrame:c.toFrame,frames:c.frames,output,sha256:v.outputSha256,narrationText:c.text,playbackSpeed:1,startedFromSeconds:0,actualEndSeconds:c.frames/60,actualEndFrame:c.toFrame-1,initialAndFinalPixelsDirectlyRead:true,observation:observations[c.id],sampledMovingPixelsApproved:true};});
const out=p+'explanation-clearance-moving-direct-review-v21.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve prior direct review');
const record={reviewedAt:new Date().toISOString(),status:'17-repaired-inputs-sampled-moving-pixels-reviewed',references:[planPath,executionPath,p+'current-input-plan-v20.json'].map(f=>({path:f,sha256:sha(f)})),
 browserUrl:'http://127.0.0.1:9265/@fs/D:/Github/Video-Editing/production/research/game-lighting-history/local/current-motion-review-v19.html',clips,
 evidenceScope:'Each input was actually started from0 at speed1 and its completed endpoint and changed visible pose were directly read. These input-page captions are DOM overlays; this is not approval of the final burned MP4, every moving frame, or human continuous listening.',
 originalPcmUnchanged:true,fixedCaptionPositionUnchanged:true,newMotionCanvasRenders:0,newGitImages:0,
 allCurrentMovingPixelsReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,humanWholeListening:'pending',humanPronunciation:'pending'};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
const cpPath='production/research/game-lighting-history/checkpoint.json',cp=read(cpPath);cp.episode03ClearanceMovingDirectReview={path:out,sha256:sha(out),clips:17,sampledMovingApproval:true,allFinalPixelsReviewed:false};cp.updatedAt=new Date().toISOString();fs.writeFileSync(path.join(root,cpPath),JSON.stringify(cp,null,2)+'\n');
console.log(JSON.stringify({directMovingInputs:17,newRenders:0,finalApproval:false}));
