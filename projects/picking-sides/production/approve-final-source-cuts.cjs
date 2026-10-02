const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!process.argv.includes('--current-source-pixels-directly-reviewed'))throw Error('Direct source action, boundaries and every cut-aware caption required.');
const index=read(path.join(work,'source-layout-review/index.json')),old=read(path.join(work,'source-layout-review-r2/index.json')),selection=path.join(work,'cut-selection.json'),s=read(selection);
if(index.selectionSha256!==hash(selection)||s.cuts.length!==45||index.samples.length!==260)throw Error('Current selection/sample mismatch');
const changed=index.samples.flatMap((v,i)=>hash(path.join(root,v.path))===hash(path.join(root,old.samples[i].path.replace('/source-layout-review/','/source-layout-review-r2/')))?[]:[i+1]);
if(JSON.stringify(changed)!==JSON.stringify([8,9,11,12,141,142]))throw Error('Unreviewed sample change');
const evidence={approved:true,at:new Date().toISOString(),selectionSha256:hash(selection),sourceBoundarySamples:135,actualCaptionSegments:125,reviewedSamples:260,firstMiddleLastAllCutsReviewed:true,everyCutAwareActualCueReviewed:true,existingGamesOnly:true,selfCreatedGameCuts:0,noLoopOrSlowdown:true,bodyRatioErrorFrames:.2,reviewMethod:'All18 R2 contact pages directly inspected; R3 six changed sample pixels directly reinspected on cut/cue contact1. Other254PNG hashes match those reviewed R2 pixels.',changedSamples:changed,findings:[
 'Trimmed authored black/lettermask10.7–13transition; replaced lost time with distinct normal-clock gripping in the same official gameplay trailer13.2–15.05.',
 'Costume example crop removes variable black side margins while keeping robot-monkey and hat-bunny identities and jumps visible.',
 'GetReady21.8 and27.1alpha starts removed; actual white-character jump39.9–44.9/27.8–29.4/58.5–59.3333 and separate later horse70–77.8333 match narration.',
 'Scene07open-space paragraph uses separate67–72.3/46–48.9/51–53.1hanging attempts rather than ground/reset frames. All sources marked as excerpts, without continuous-match inference.',
 'Scene09space movement and scene11red drop are arranged sharply in upper870px over a full-screen source-filled background to preserve character/flames/hands below the camera while all captions stay960,970. No white PPT frame.',
 'Scene11separate scaffold102–107.6667keeps hand/platform action and excludes the previous ground/reset. Next107.82–117.8033red hand/drop matches observed outcome; no overall-winner claim.'
 ],humanListening:'pending',publicRights:'pending',finalRenderedPixelReview:'pending'};
fs.writeFileSync(path.join(work,'final-source-cut-review.json'),JSON.stringify(evidence,null,2)+'\n');
index.status='passed-direct-source-action-boundary-and-every-actual-caption-preview-review';index.reviewedAt=evidence.at;index.samples.forEach(v=>{v.sha256=hash(path.join(root,v.path));});fs.writeFileSync(path.join(work,'source-layout-review/index.json'),JSON.stringify(index,null,2)+'\n');
console.log('Exact45-cut source gate recorded; final encoded media/caption pixel QA remains required.');
