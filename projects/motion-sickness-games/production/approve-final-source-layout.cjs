// Approval records only the source pixels actually inspected. Encoded chapter
// and final presentation/caption QA remain separate, mandatory gates.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const selection=path.join(work,'cut-selection.json'),layoutFile=path.join(work,'caption-layout-qa.json'),indexFile=path.join(work,'source-layout-review/index.json');
const cuts=read(selection).cuts,layout=read(layoutFile),index=read(indexFile),voice=read(path.join(__dirname,'voice-approval.json'));
if(!voice.allCurrentScenesTechnicallyReviewed||index.selectionSha256!==sha(selection))throw Error('Current exact selection/voice review required');
if(cuts.length!==34||index.sourceBoundarySamples!==102||index.actualCaptionSegments!==119||index.samples.length!==221)throw Error('Directly reviewed inventory changed');
if(layout.cueCount!==166||layout.segmentCount!==174||layout.cues.some(c=>c.centerX!==960||c.centerY!==970||c.overlap))throw Error('Fixed caption layout failed');
for(const s of index.samples)if(!fs.existsSync(path.join(root,s.path)))throw Error('Missing inspected pixels');
const result={kind:'direct-current-source-action-and-every-actual-caption-segment-review',createdAt:new Date().toISOString(),approved:true,
 selectionSha256:sha(selection),layoutSha256:sha(layoutFile),indexSha256:sha(indexFile),voiceApprovalSha256:sha(path.join(__dirname,'voice-approval.json')),
 sourceBoundarySamples:102,actualCaptionSegments:119,totalDirectlyReadImages:221,
 inspectedPages:index.pages.map(p=>({path:p,sha256:sha(path.join(root,p))})),
 findings:[
  'All34 excerpts are normal-speed actual PowerWash Simulator or Talos2 play. Source intervals are unrepeated, full-screen, and exclude the researched menus/notifications/title/snow/idle/outro ranges.',
  'Source labels identify the2022 FuturLab WIP and2023 official Talos2 material. Separate excerpts are explicitly described as separate, with no controlled comfort/health experiment claim.',
  'Initial wide-caption source review rejected bottom-left tool-selector overlap. All current PWS cues were shortened/wrapped with a900px text bound while retaining48px font and the exact960,970 center; the tool selector and right stance UI are visible.',
  'Initial07p4 source stayed skyward under board/post nouns and was rejected. Current251.5,265,289 excerpts follow look-up, turn back, and board/post landmark observation in the measured narration.',
  '07 final normal-speed view turn toward the fence supports the heading/remaining-landmark observation question; it is not described as washing.',
  'Cue59 source313.881667 andcue60 source317.321667 are monotonic. The small contact annotation was rechecked against the index; no retiming was needed.',
  'Spray destination, target geometry, roundabout, slide, posts, overhead crossbars, Talos devices/laser and environmental direction cues remain visible in each inspected caption segment.'
 ],initialRejectedReview:'projects/motion-sickness-games/production/final-v1/source-layout-review-initial-wide-cues/index.json',
 eachCut:cuts.map(c=>({id:c.id,sourceId:c.sourceId,in:c.sourceIn,out:c.sourceOut,frames:c.frames,actionAndNarrationFit:true,firstMiddleLastDirectlyRead:true})),
 captionCenter:[960,970],encodedChapterBoundaryReview:'pending',allFinalCaptionPixelsIncludingPPT:'pending',wholeFinalDecode:'pending',humanListening:'pending',finalPublicRights:'pending',finalVideoApproved:false};
fs.writeFileSync(path.join(work,'final-source-cut-review.json'),JSON.stringify(result,null,2)+'\n');
console.log('Approved exact102 source boundaries and119 actual caption segments; encoded/final QA pending.');
