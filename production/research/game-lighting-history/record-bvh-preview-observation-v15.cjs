const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod=path.join(root,'projects/game-lighting-history-03/production');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const target=path.join(prod,'bvh-sampled-preview-observation-v15.json');
if(fs.existsSync(target))throw Error('Preserve recorded direct observation');
const proofPath=path.join(__dirname,'local/explanation-framing-v15/silent-review-visual-v15.verification.json');
const proof=read(proofPath);
if(proof.outputSha256!=='a47e4b5b64782a64ce21fd88ad47344fcc4f65e6e96284db931e4511fd99f565')throw Error('Different review visual');
const record={reviewedAt:new Date().toISOString(),browserId:'4',tabId:'16',method:'CUA browser playback and sampled screenshots; no screenshot saved',
 source:proof.output,sourceSha256:proof.outputSha256,verificationSha256:hash(proofPath),
 observations:[
  {seconds:178.733333,visible:'Parent-box branch-elimination heading; teal projected box/triangle and ray; non-unit direction explicitly warns t is not metres.'},
  {seconds:207.530396,visible:'Transition heading [4,5]에서 겹침 없음으로. Axes x=[2,6], y=[3,5], z=[4,7], common=[4,5]. This is the starting overlap state, not an incorrect final miss claim.'},
  {seconds:215,visible:'Moving box and its z interval update together; z=[4.6,7.3], common=[4.6,5.0].'},
  {seconds:218,visible:'Red displaced projected box; z=[7.3,8.7], no common interval because 7.3>5.0.'},
  {seconds:218.7,visible:'Actual paused video time and readyState=4 verified after seek. Final z=[8.0,9.0]; no common interval because 8.0>5.0. Ray and triangle remain spatially distinct.'}
 ],
 scope:'Sampled spatial/numeric transition observation only; the complete narrated pair and all final burned-caption pixels remain separate review gates.',
 continuousAllMotionReviewed:false,narratedPlaybackReviewed:false,burnedCaptionPixelsReviewed:false,
 allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newRasterImages:0,mediaCreated:0};
fs.writeFileSync(target,JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({record:target,sampledSpatialTransitionConsistent:true,allFinalPixelsReviewed:false,imagesCreated:0}));
