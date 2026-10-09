const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now = new Date().toISOString();
const records = [
  ['23-mining-and-pursuit','23-f10010.png',10010,'23-f10211.png',10211,'Approach toward the mineral, pursuer changes position, rock faces occlude the ground path and actors; distinct approach and avoidance relations.'],
  ['24-destination-and-danger','24-first.png',10403,'24-second.png',10564,'Actor travels toward and enters the projected circle; nearby actors remain and move after arrival. No victory result is shown or asserted.'],
  ['25-gap-during-pursuit','25-first.png',10806,'25-second.png',11028,'Actor and pursuer move through a narrow rock gap; front rock occludes the path, which reappears beyond it.']
].map(([id,a,af,b,bf,observation]) => ({id,observation,frames:[[a,af],[b,bf]].map(([file,frame])=>{
  const p='shared/output/similar-game-design/spatial-lookdev-v3/'+file;
  return {path:p,sha256:sha(p),actualPreviewFrame:frame,directlyRead:true,localOnly:true};
})}));
const code = ['motion-canvas/src/projects/similar-game-design/spatial-explanation-v1.tsx','motion-canvas/src/projects/similar-game-design/authoring-project-v1.ts','motion-canvas/src/projects/similar-game-design/authoring-timing-v1.json', ...records.map(x=>'motion-canvas/src/projects/similar-game-design/scenes/'+x.id+'.tsx')].map(p=>({path:p,sha256:sha(p)}));
const review = {schemaVersion:1,reviewedAt:now,records,code,previewFps:30,actualDistinctFrames:6,allNewAnimatedLookdevPixelsDirectlyRead:true,projectedTopSideFrontFaces:true,depthSortedOcclusion:true,meaningfulRelationshipMotion:true,measuredNarrationTimingApplied:false,finalTimingApproved:false,allFinalParagraphPixelsReviewed:false,finalRenderApproved:false,imagesGitAdded:0,scope:'Unmeasured layout and motion preview only. It does not approve final 60fps encoded pixels, narration timing, captions, source allocation or final pair.'};
const out='projects/similar-game-design/production/three-guide-spatial-lookdev-direct-review-v3.json';
if(fs.existsSync(path.join(root,out))) throw new Error('Existing direct review must be preserved.');
fs.writeFileSync(path.join(root,out),JSON.stringify(review,null,2)+'\n');
const prepPath=path.join(__dirname,'three-guide-spatial-lookdev-preparation-v3.json');
const prep=JSON.parse(fs.readFileSync(prepPath,'utf8'));prep.allNewAnimatedPixelsReviewed=true;prep.directReview=out;prep.directReviewSha256=sha(out);prep.reviewedAt=now;
fs.writeFileSync(prepPath,JSON.stringify(prep,null,2)+'\n');
const cpPath=path.join(__dirname,'latest-checkpoint.json');const cp=JSON.parse(fs.readFileSync(cpPath,'utf8'));
cp.motionCanvas.independentScenes=24;cp.motionCanvas.freshGuideLookdevReview=out;cp.motionCanvas.freshGuideLookdevFrames=6;cp.motionCanvas.totalLookdevFrames=49;cp.motionCanvas.finalMeasuredPixelsReviewed=false;
fs.writeFileSync(cpPath,JSON.stringify(cp,null,2)+'\n');
console.log('Six new animated lookdev states directly read and hashed; final timing/caption/pixel gates remain false.');
