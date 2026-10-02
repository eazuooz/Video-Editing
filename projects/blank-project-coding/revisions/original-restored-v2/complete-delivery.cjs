const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const W=__dirname,R=path.resolve(W,'../../../..'),receiptPath='projects/blank-project-coding/publishing/youtube-upload-original-restored-v2.json';
const r=JSON.parse(fs.readFileSync(path.join(R,receiptPath),'utf8'));
assert.equal(r.videoId,'bbpKRhlxeCs');assert.equal(r.metadata.privacyStatus,'private');
assert(r.uploadedCaptionVerification.passed&&r.subtitles.every(s=>s.status.includes('published')));
assert(r.coachingCard.status.includes('verified')&&r.coachingEndingLink.status.includes('verified'));
for(const file of [path.join(W,'final.manifest.json'),path.join(R,'projects/blank-project-coding/project.json')]){
 const m=JSON.parse(fs.readFileSync(file,'utf8'));
 m.status='original-restored-v2-rendered-reviewed-collected-and-private-uploaded';
 m.production={...m.production,currentStage:'private-upload-settings-complete-git-delivery-pending',rendered:true,collected:true,uploaded:true};
 m.publishing={...(m.publishing||{}),receipt:receiptPath,videoId:r.videoId,videoUrl:r.videoUrl,privacyStatus:'private',publicPublishReady:false,pinnedCommentStatus:'pending-video-publication'};
 m.approvals.platform='Private upload, HD burned captions with CC off, manualKO/EN subtitles, English metadata, coaching card and three ending elements verified. Ads enabled; exact automatic-review observations retained in receipt.';
 fs.writeFileSync(file,JSON.stringify(m,null,2)+'\n');
}
const cp=JSON.parse(fs.readFileSync(path.join(W,'checkpoint.json'),'utf8'));
cp.stage='private-upload-settings-complete-git-delivery-pending';cp.updatedAt=new Date().toISOString();
cp.videoId=r.videoId;cp.uploadReceipt=receiptPath;cp.remaining=['Metadata-only Git commit and push'];
cp.pendingHumanOrPlatform=['Full human listening','Public review of source rights and restored Nimbus original-byte acquisition','External media backup destination','Post and pin drafted coaching comment once user makes comments available','Separate final automatic ad-review decision: latest actual UI evidence retained in receipt'];
cp.completed.push('77473-frame clean and burned final full decode and copied-audio verification','All134 cuts,582 caption placements and182 composition samples directly reviewed; repaired Tetris dense-review passed','Current root output collection and private upload bbpKRhlxeCs','HD1080p60 burned Korean caption visible with playerCCoff','KO/EN manual subtitle publication, English metadata, coaching card00 and final10s three-element end screen saved/reopened verified');
fs.writeFileSync(path.join(W,'checkpoint.json'),JSON.stringify(cp,null,2)+'\n');
console.log('Private upload completion linked to current project; human/public pending items preserved.');
