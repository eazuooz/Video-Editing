const fs=require('fs'),crypto=require('crypto'),path=require('path');
const root=path.resolve(__dirname,'../../..'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
for(const version of ['v1','v2']){
 const file=`projects/game-reward-planning/production/lookdev-${version}/inspection.json`,r=JSON.parse(fs.readFileSync(path.join(root,file),'utf8'));
 if(r.directVisualReview!=='pending')throw Error('Preserve recorded review '+version);
 if(sha(r.source)!==r.sourceSha256||r.frames.length!==28||r.fullDecodeExitCode!==0)throw Error('Incomplete current evidence');
 r.directVisualReview=version==='v1'?'rejected-two-arrow-layout-issues':'passed-silent-layout-only';
 r.reviewedAt=new Date().toISOString();r.all28ViewsDirectlyRead=true;
 r.assessment=version==='v1'?'Scene05 early first arrow collapsed/reversed into a short mark; scene13 diagonal arrows crossed the red caution text. Preserve this render and use v2.':'All seven explanations in early/middle/late and transition views were directly inspected. Scene05 first connector has readable forward direction; scene13 branch arrows route below the red caution line. Text, spacing, contrasts and diagram relations remain legible in every sampled layout.';
 r.scope='Silent seven-scene 56-second/3360-frame layout only. Narrated paragraph timing, fixed captions, actual footage and final video remain unapproved.';
 r.finalNarratedVideo=false;r.finalCaptionApproval=false;r.scopedTypeScriptCheck={command:'node motion-canvas/node_modules/typescript/bin/tsc -p projects/game-reward-planning/production/tsconfig.review.json --noEmit',exitCode:0,globalTypeScriptPass:false};
 fs.writeFileSync(path.join(root,file),JSON.stringify(r,null,2)+'\n');
}
const state=JSON.parse(fs.readFileSync(path.join(root,'projects/game-reward-planning/production/speech-v2/execution.json'),'utf8'));
fs.writeFileSync(path.join(root,'projects/game-reward-planning/production/speech-v2/launch.json'),JSON.stringify({sessionId:73585,pid:state.pid,workerPid:state.workerPid,command:state.command,state:'projects/game-reward-planning/production/speech-v2/execution.json',log:'projects/game-reward-planning/production/composite-v2-runner.log',observedAt:new Date().toISOString()},null,2)+'\n');
console.log('v1 rejected/v2 silent-layout review recorded; current CPU ASR launch preserved.');
