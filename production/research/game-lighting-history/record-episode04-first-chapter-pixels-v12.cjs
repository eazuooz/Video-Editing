const fs = require('node:fs'), crypto = require('node:crypto');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const base = 'projects/game-lighting-history-04/production/';
const out = base + 'first-chapter-encoded-direct-review-v12.json';
if (fs.existsSync(out)) throw Error('Preserve recorded direct review');
const buildPath = base + 'first-chapter-review-build-v12.json';
const extractionPath = 'production/research/game-lighting-history/local/episode04-first-chapter-encoded-v12/execution.json';
const b = read(buildPath), e = read(extractionPath);
if (e.status !== 'encoded-samples-ready' || e.active || e.commands.some(x => x.exitCode !== 0)) throw Error('Incomplete extraction');
if (e.items.length !== 263 || e.boards.length !== 67) throw Error('Unexpected scope');
for (const x of [...b.outputs, ...e.items, ...e.boards]) if (sha(x.path) !== x.sha256) throw Error('Changed input: ' + x.path);
if (!b.identicalAacPayload || !b.identicalAacToV11 || b.outputs.some(x => x.frames !== 11664 || x.wholeDecode.exitCode !== 0)) throw Error('Technical pair changed');
const r = {
  recordedAt: new Date().toISOString(),
  scope: 'First194.4s only; encoded sparse review of all12 changed cuts and adjacent boundaries. Unchanged interiors retain v11 review. This is not continuous playback or whole-episode approval.',
  build: {path:buildPath, sha256:sha(buildPath)},
  extraction: {path:extractionPath, sha256:sha(extractionPath), sessionId:76236, exitCode:0, worker:e.worker},
  directReview: {cleanBoards:13, captionedBoards:54, imagesRepresented:263, allBoardsDirectlyViewed:true, reviewContinuedAcrossTurns:true},
  boards: e.boards.map(x => ({...x, directlyViewed:true})),
  captionScope: {totalFirstChapterCues:44, changedCutCuesAndAdjacentBoundariesRead:true, unchangedInteriorEvidence:base+'first-chapter-encoded-direct-review-v11.json', center:[960,970], fontSize:48, maximumLines:2, noCaptionPositionChange:true},
  findings: [
    {id:'retained-model-footers', observed:'Nine existing model pictures shifted up60px. Sampled yellow headings, projected top/side faces, arrows, numeric examples and secondary caveats remain in-frame; bottom footers are clear above fixed two-line captions. Blank top crop retained all observed content.', sampledClearanceApproved:true},
    {id:'cyber-original-label-strip', observed:'Original same-frame Off/DLSS3.5 labels duplicated above fixed cue6. Bottom original labels remain; wet-ground footage is a manufacturer bundled-feature example, not an isolated RR or FPS test.', sampledClearanceApproved:true},
    {id:'renderdoc-original-values', observed:'Same-frame input/output table magnified above cue7/8; COLOR(.96125,.01312,.02562,1) and initial zero output followed by equal output are readable. Frame622/EID14 remain visible. Original horizontal scroll truncates output-name prefixes later; missing text was not reconstructed.', sampledClearanceApproved:true, caveat:'Persistent return underline is an operation identifier, not the current execution pointer. Orange output box begins at local2.5s, later than the first observed changed output; do not claim exact debugger-step timing.'},
    {id:'vsm-distinct-excerpts', observed:'Boundary samples retain different-excerpts label. Wheel-shadow and later museum/city are distinct source cuts. Debug color is not illumination; source pixels do not measure page counts, memory updates or FPS.'},
    {id:'smrt-independent-geometry', observed:'Projected blocker/receiver and colored sample rays remain above captions. Independent illustrative five-ray example and depth-map-vs-all-scene-triangles caveat readable; cache comparison changes green reuse/orange new/red invalidation without footer obstruction.'}
  ],
  supersedesOnlyObservedClearanceFailures:base+'first-chapter-encoded-direct-review-v11.json',
  preservedTiming: {frames:11664, seconds:194.4, sourceModelsRerendered:0, newTts:0, sameCaptionAss:true, identicalAacToV11:true},
  packetEvidenceCaveat:'All presentation PTS are continuous at1500ticks/timebase90000; available packet durations agree. Duration fields missing in9158 clean and11664 captioned packets remain missing, not inferred as observed.',
  allFirstChapterSampledPixelsRead:true,
  firstChapterSampledCaptionClearanceApproved:true,
  allFinalPixelsReviewed:false, allMovingPixelsReviewed:false, causalFlowApproved:false,
  finalMixedAsrApproved:false, wholeEpisode60to40Approved:false, qaApproved:false, collected:false, uploaded:false,
  humanWholeListening:'pending', newGitImages:0,
  next:'Continue remaining99 paragraph composition with directly observed official TSR/mannequin/fan examples; normal continuous encoded playback and tracked annotations remain required.'
};
fs.writeFileSync(out,JSON.stringify(r,null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json', j=read(cp);
j.episode04FirstChapterDirectPixelReview={path:out,sha256:sha(out),sampledBoardsRead:67,sampledCaptionClearanceApproved:true,allFinalPixelsReviewed:false,next:r.next};
j.ownedActiveWork={status:'no-active-owned-media-worker',lastExecution:extractionPath,sessionId:76236,exitCode:0,next:r.next};
j.updatedAt=r.recordedAt;fs.writeFileSync(cp,JSON.stringify(j,null,2)+'\n');
console.log(JSON.stringify({record:out,boards:67,images:263,sampledCaptionClearanceApproved:true,allFinalPixelsReviewed:false}));
