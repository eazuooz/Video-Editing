// Save the completed direct source-pixel review; final encoding QA remains separate.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const read=f=>JSON.parse(fs.readFileSync(path.join(work,f),'utf8'));
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(work,f))).digest('hex');
const write=(f,v)=>fs.writeFileSync(path.join(work,f),JSON.stringify(v,null,2)+'\n');
const ix=read('source-layout-review-v3/index.json'),selection=read('cut-selection.json'),layout=read('caption-layout-qa.json');
if(fs.existsSync(path.join(work,'final-source-cut-review.json')))throw Error('Preserve existing review.');
if(ix.selectionSha256!==sha('cut-selection.json')||ix.layoutSha256!==sha('caption-layout-qa.json'))throw Error('Reviewed pixels changed.');
if(ix.sourceBoundarySamples!==138||ix.actualCaptionSegments!==267||ix.samples.length!==405||selection.cuts.length!==46)throw Error('Unexpected review inventory.');
for(const s of ix.samples)if(!fs.existsSync(path.join(root,s.path)))throw Error('Missing reviewed view:'+s.path);
const now=new Date().toISOString(),detail={
 reviewedAt:now,status:'all-current-source-v3-preview-pixels-directly-reviewed',
 selectionSha256:sha('cut-selection.json'),layoutSha256:sha('caption-layout-qa.json'),indexSha256:sha('source-layout-review-v3/index.json'),
 sourceBoundaryViewsDirectlyRead:138,actualCaptionViewsDirectlyRead:267,contactPagesDirectlyRead:35,allViewsReviewed:true,
 fullResolutionRechecks:['cue-8-8.png','cue-48-51.png','cue-58-61.png','cue-87-91.png','cue-131-135.png','cue-165-173.png','cue-225-237.png','cue-268-282.png'],
 observations:[
  'Every one of46 first/middle/last native source views and267 cut-aware Korean cue midpoints was directly read in35 contact pages. Eight control/price/placement/arrow cases were reopened at full resolution.',
  'All game pixels fill1920x1080 from the face-free1376x774 source crop. The v2 inset-like foreground was rejected and is preserved as historical evidence.',
  'Single-line short cues keep boxed-white-forest-v1 at960,970 and48px. Observed menus, price readouts, selected handles and collision lists remain clear; no caption position was moved.',
  'Entrance-close wording now has gate pixels at4626.4–4628.4 and4632–4633.2. Later wider shots accompany the reference relationship, without implying a completed ride.',
  'The scene11 return/selection wording now shows red track, selectable controls and support adjustment at3207.5–3217.4167 and3233.25–3237.9. Different source passages are identified as separate excerpts.',
  'Catalog/HireStaff/unrelated green-coaster windows remain excluded. Gold flower, lamp and balloon are distinct decoration passages; narration does not infer satisfaction or automatic rule movement.'
 ],
 unresolvedTemporalReview:{finalRenderedCaptionStartsAndEnds:'pending',shortWordCues:[{cue:148,text:'알아야,',seconds:0.447},{cue:226,text:'줄 수',seconds:0.307},{cue:256,text:'모양이',seconds:0.387}],humanPlaybackReadability:'pending',note:'Current review approves source allocation and static caption clearance for audio-free compilation only. Short displayed phrases need temporal review before final caption approval.'},
 captionCenter:[960,970],allCutsApprovedForAudioFreeEncoding:true,body60_40Passed:false,allFinalCaptionPixelsReviewed:false,finalVideoApproved:false
};
write('source-layout-review-v3/direct-review.json',detail);
write('final-source-cut-review.json',{
 approved:true,approvalScope:'exclusive normal-speed audio-free source encoding; not final narrated-video approval',reviewedAt:now,
 selectionSha256:detail.selectionSha256,layoutSha256:detail.layoutSha256,reviewIndexSha256:detail.indexSha256,
 directReview:'projects/hierarchical-game-outlines/production/final-v1/source-layout-review-v3/direct-review.json',
 allCurrentActualCaptionSegmentsDirectlyReviewed:true,allNativeBoundariesDirectlyReviewed:true,
 sourceCuts:46,nativeBoundaryViews:138,actualCaptionSegments:267,captionCenter:[960,970],
 actualTargetSeconds:344.85,explanationTargetSeconds:229.9,body60_40Passed:false,
 allEncodedNativeBoundaryPixelsReviewed:false,allFinalCaptionPixelsReviewed:false,finalVideoApproved:false,
 pending:['encoded source boundaries','short-word cue temporal review','every final actual/PPT cue','full audio/mix/render QA']
});
console.log(JSON.stringify({sourceCutsApprovedForEncoding:46,previewViewsDirectlyRead:405,finalVideoApproved:false}));
