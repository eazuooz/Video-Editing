const fs=require('fs'),crypto=require('crypto');
const b='production/research/game-lighting-history',p='projects/game-lighting-history-04/production/word-clock-encoded-direct-review-v3.json',r=JSON.parse(fs.readFileSync(p,'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(sha(r.media.path)!==r.media.sha256||!r.all103EncodedSamplesDirectlyRead||!r.all26BoardsDirectlyRead)throw Error('Current encoded pixel evidence required');
const out='projects/game-lighting-history-04/production/word-clock-normal-playback-review-v3.json';
if(fs.existsSync(out))throw Error('Preserve actual playback record');
const scenes=[
 {scene:0,observedSeconds:[0,13.764],observation:'Normal-rate encoded video progressed from the initially empty projected grid to32 versus8 tiles, opposite arrows and the fixed Korean caption. Exact transition is established separately by encoded frames907/908, not the async browser clock.'},
 {scene:1,observedSeconds:[15.144,22.977,25.503],observation:'Normal-rate progression shows the inside-tile teal transfer arrow during conditional local-memory narration; outside transfer and caption boundaries are independently covered by the encoded pixel record. No GPU measurement inferred.'},
 {scene:2,observedSeconds:[31.879,44.569,44.596],observation:'The brighter direction example reveals8×0.5÷0.8=5 at its narration stage while the later dark formula is still absent; both branch arrows and the fixed caption remain readable.'},
 {scene:3,observedSeconds:[53.457,67.005],observation:'Normal-rate encoded progression reveals continuation and termination branches before the full expectation equation0.8×1.25+0.2×0=1. Later-stage screenshot has both branches and readable fixed two-line narration.'},
 {scene:4,observedSeconds:[71.562,79.532,80.329],observation:'The red-front example appears first with0.5/0.25 bars while the reverse-order result is still absent. Projected front-layer occlusion remains visible. The natural inter-cue gap is not a missing-caption assertion.'},
 {scene:5,observedSeconds:[84.817,85.033,93.761733,98.983333],observation:'At normal rate the top row reaches1R+3G=4 and the bottom row is still adding its green generated blocks; the terminal encoded frame has1R+5G=6. The orange rendered-frame tick stays a single tick in both rows. Two-line fixed caption distinguishes displayed counts from simulation updates/FPS.'}
];
fs.writeFileSync(out,JSON.stringify({reviewedAt:new Date().toISOString(),method:'CUA browser4/tab32 actual encoded HTML video, muted, playbackRate1; direct screenshots plus read-only video clock',media:r.media,encodedPixelEvidence:{path:p,sha256:sha(p)},scenes,allSixNormalRateMotionSamplesReviewed:true,continuousAllFramesViewed:false,audioHeard:false,technicalProofMotionApproved:true,finalAllPixelsApproved:false,finalTimingApproved:false,finalMixedAudioApproved:false,humanListeningApproved:false,newGitImages:0},null,2)+'\n');
const cpPath=b+'/checkpoint.json',c=JSON.parse(fs.readFileSync(cpPath,'utf8'));
c.wordClockNormalPlaybackV3={path:out,sha256:sha(out),technicalProofMotionApproved:true,allFinalPixelsApproved:false};
c.next='Six current numerical proof scenes have direct encoded pixels and normal-rate motion samples. Complete exact native cuts and111 independent paragraph scenes; then measure60:40/final mix/current mixed ASR/whole decode/final pixels/output/private/Git.';
c.updatedAt=new Date().toISOString();fs.writeFileSync(cpPath,JSON.stringify(c,null,2)+'\n');
console.log(JSON.stringify({out,scenes:6,technicalMotionApproved:true,finalApproved:false}));
