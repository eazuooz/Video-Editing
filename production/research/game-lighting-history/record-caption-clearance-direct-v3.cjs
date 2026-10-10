const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const prod = 'projects/game-lighting-history-03/production';
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const executionPath = `${prod}/caption-clearance-pixel-execution-v3.json`;
const outputPath = `${prod}/caption-clearance-direct-review-v3.json`;
if (fs.existsSync(path.join(root,outputPath))) throw Error('Preserve existing direct review.');
const execution = read(executionPath);
if(execution.status !== 'complete' || execution.exitCode !== 0 || execution.boards.length !== 44 || execution.images.length !== 264) throw Error('Incomplete extraction.');
if(execution.sourceSha256 !== '0d679faa0e3eb073bbcd6e565eef6e603bea4f13ab7a595d8c093d02a3b21779' || sha(execution.source) !== execution.sourceSha256) throw Error('Reviewed source changed.');
if(execution.originalCaptionAssSha256 !== '0989880d19c045e1e3d4e0bca6ee7f9014446819dfbfbb67064b5dd84d9b251b') throw Error('Captions changed.');
const observations = {
  'original-39': 'Projected wall/receiver A/B comparisons both show E=6.00; two-probe principle example and actual DDGI distance moments, normal, bias and eight-point interpolation caveat remain visible above fixed captions 157–159.',
  'original-40': 'Occluded probe B contribution fades; right E moves 6.00 → 4.68 → 2.05 → 2.00 while left remains 6.00. Captions 160–162 and DDGI caveat remain distinct.',
  'original-44': 'Four labelled lights/arrows feed reservoir M/W states 0/0 → 1/1 → 2/4 → 3/5 → 4/6. The 2020 direct-light versus later GI/PT distinction and simplified-example caveat remain visible above captions 183–186.',
  'original-45': 'Projected weight bars 1 and 3 show P=3/(1+3)=0.75. Four displayed equal-spaced u values select B/B/B/A; text explicitly distinguishes this illustration from random-run statistics and a complete ReSTIR estimator. Captions 187–189 remain clear.',
  'original-46': 'Three spatial q/target/M blocks and staged arrows distinguish candidate selection from the final estimate; normalization, visibility and reuse caveats remain readable above captions 190–192.',
  'original-47': 'Spatial neighbours and a prior-frame dotted arrow feed the current receiver; the visible normal/position/visibility revalidation caveat is not covered by captions 193–195.',
  'original-48': 'Door closes between receiver and light, changing pass to occluded and hiding the light path; the old-brightness-copy warning remains visible above captions 196–198.',
  'original-52': 'Projected 4×4 depth grid marks eight red rejected cells and eight teal retained cells. Front depth 0.3 < back sample 0.8 and shader-condition limitation remain visible above captions 213–215.',
  'original-53': '4×4 → 2×2 max-depth summary 0.3/0.4/0.5/0.8 shows near=0/far=1 and candidate 0.9 > 0.8. Fully covered, empty-far=1 and reversed-Z min/comparison caveats all remain above captions 216–218.',
  'original-54': 'Door movement reveals a teal object that the old red mask would hide; current-versus-old depth and non-engine-specific caveats remain clear above captions 219–221.',
  'original-56': 'Four projected mesh groups show one becoming dark; text distinguishes geometry work from GI. Captions 230–232 remain clear.',
  'original-57': 'The same sixteen output cells retain their grid while sixteen orange independent evaluations become four teal 2×2 evaluations; explicit output-grid/evaluation-location distinction remains clear above captions 233–235.',
  'original-58': 'One projected 2×2 evaluation shares with four cells. Support, interpolation and coverage limitations and the warning against assuming four-times whole-frame speed remain visible above captions 236–239.',
  'original-59': 'Five highlighted pages in a 64-page grid correspond to resident IDs 9/10/11/18/27; the distinction from learned texture creation stays visible above captions 240–242.',
  'original-60': 'Four orange requested pages become zero, two then four teal arrived pages; latency, memory and fallback-mip text remain visible above captions 243–245.',
  'original-65': 'ep≈f·e_world/d uses labelled units, f=1000px and e=0.01m; d≈2→4m and ep≈5→2.50px progress coherently. Rounded-display/pinhole approximation and incomplete-Nanite-rule caveats remain visible above captions 277–279.',
  'original-81-explanation': 'Four projected cache groups highlight staged tracing/storage/partitioned updates. Text explicitly calls the four groups an independent diagram rather than measured Lumen updates/frame count; captions 345–346 remain clear.'
};
const records = execution.boards.map((board, i) => {
  if(sha(board.path)!==board.sha256) throw Error(`Board ${i+1} changed.`);
  const images = board.imageIndices.map(n => execution.images[n-1]);
  for(const image of images) if(sha(image.path)!==image.sha256) throw Error('Reviewed frame changed.');
  const inputs = [...new Set(images.map(q => q.input))];
  for(const input of inputs) if(!observations[input]) throw Error(`Missing observation ${input}.`);
  return {boardIndex:i+1,board:board.path,boardSha256:board.sha256,directlyRead:true,
    images:images.map(q=>({index:q.index,path:q.path,sha256:q.sha256,originalFrame:q.frame,repairFrame:q.repairFrame,input:q.input,cueIds:q.visibleCueIds})),
    observations:inputs.map(input=>({input,observation:observations[input]})),unresolved:[]};
});
const review = {recordedAt:new Date().toISOString(),scope:'Direct reading of all 44 contact boards / 264 exact changed-explanation frames in this continuing review; not whole final encoded pair or full motion playback.',
  source:execution.source,sourceSha256:execution.sourceSha256,extraction:executionPath,extractionSha256:sha(executionPath),
  originalCaptionAssSha256:execution.originalCaptionAssSha256,boardsDirectlyRead:44,imagesDirectlyRead:264,changedExplanationCount:17,
  allChangedBoardsDirectlyRead:true,changedSampleCaptionClearanceApproved:true,fixedCaptionPosition:[960,970],records,
  boundaryObservations:[{lastFrame:41776,nextFrame:41777},{lastFrame:48917,nextFrame:48918},{lastFrame:56114,nextFrame:56115},{lastFrame:60892,nextFrame:60893}],
  fullAnimatedPlaybackReviewed:false,allFinalPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,newGitImages:0,
  pending:['Direct animated playback of changed explanation motions','Unrelated remaining one-frame explanation tails','Actual-footage interval and source-UI repairs','Both final encoded-pair and whole-video technical/content review','Human full listening/pronunciation and rights review']};
fs.writeFileSync(path.join(root,outputPath),JSON.stringify(review,null,2)+'\n');
const checkpointPath = 'production/research/game-lighting-history/checkpoint.json';
const checkpoint = read(checkpointPath);
checkpoint.episode03CaptionClearanceDirectReview = {path:outputPath,sha256:sha(outputPath),boards:44,images:264,changedExplanations:17,changedSampleCaptionClearanceApproved:true,allFinalPixelsReviewed:false};
checkpoint.episode03CaptionClearancePixelExecution = {path:executionPath,status:execution.status,exitCode:execution.exitCode,completedAt:execution.completedAt,session:25908,workerObservedAbsent:true,gpuJobs:0,cpuThreads:2};
checkpoint.stage = 'episode03-native-interval-ui-repair';
checkpoint.ownedActiveWork = null;
checkpoint.ownJobs = [];
checkpoint.updatedAt = new Date().toISOString();
checkpoint.nextAction = 'Continue direct actual-source playback and replace promotional/unclear/incorrect intervals; retain all approved PCM/timing and 17 reviewed explanation repairs. Complete animated and final pair review before collection/upload.';
const dest=path.join(root,checkpointPath),tmp=dest+'.writing-'+process.pid;
fs.writeFileSync(tmp,JSON.stringify(checkpoint,null,2)+'\n');fs.renameSync(tmp,dest);
console.log(JSON.stringify({review:outputPath,boards:44,images:264,changedExplanations:17,allFinalPixelsReviewed:false}));
