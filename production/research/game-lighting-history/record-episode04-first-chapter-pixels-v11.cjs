const fs = require('node:fs'), crypto = require('node:crypto');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const base = 'projects/game-lighting-history-04/production/';
const out = base + 'first-chapter-encoded-direct-review-v11.json';
if (fs.existsSync(out)) throw Error('Preserve recorded direct review');
const buildPath = base + 'first-chapter-review-build-v11.json';
const extractionPath = 'production/research/game-lighting-history/local/episode04-first-chapter-encoded-v11/execution.json';
const b = read(buildPath), e = read(extractionPath);
if (e.status !== 'encoded-samples-ready' || e.active || e.commands.some(x => x.exitCode !== 0)) throw Error('Incomplete extraction');
if (e.items.length !== 290 || e.boards.length !== 73) throw Error('Unexpected scope');
for (const x of [...b.outputs, ...e.items, ...e.boards]) if (sha(x.path) !== x.sha256) throw Error('Changed input: ' + x.path);
const r = {
  recordedAt: new Date().toISOString(),
  scope: 'First194.4s only; sparse encoded cue/cut review, not continuous playback or whole-episode approval',
  build: {path: buildPath, sha256: sha(buildPath)},
  extraction: {path: extractionPath, sha256: sha(extractionPath), sessionId: 56930, exitCode: 0, worker: e.worker},
  directReview: {cleanBoards: 8, captionedBoards: 65, imagesRepresented: 290, allBoardsDirectlyViewed: true, reviewContinuedAcrossTurns: true},
  boards: e.boards.map(x => ({...x, directlyViewed: true})),
  cueScope: {count: 44, firstMiddleLastBeforeAfterRead: true, captionCenter: [960,970], fontSize:48, maximumLines:2, fixedBoxReadableInSamples:true, timingAndWholeListeningApproved:false},
  findings: [
    {id:'model-footer-overlap', affectedCuts:['original-overview-1','original-18v-1','original-18v-2','02-pre-vsm-address','original-18v-3','original-18v-4','original-18v-5','original-18v-6','original-18v-7'], observed:'Secondary explanatory footer around nativey892 is partly covered by two-line captions. Main formulas, projected faces and semantic colors remain visible.', repair:'Shift retained model picture up60px by cropping only the blank top60px and padding black at bottom. Preserve timing, all explanation and animation; inspect resulting encoded pixels.'},
    {id:'cyber-label-overlap', cut:'overview-cyber', frames:[1546,1732], observed:'Original DLSSOff/DLSS3.5 split labels at bottom are covered by cue6 until28.88s.', repair:'Copy the original same-frame label strip to the upper image. Keep manufacturer combined-feature caveat; do not claim isolated RR/FPS comparison.'},
    {id:'renderdoc-values-overlap', cuts:['overview-renderdoc','original-silent-boundary'], observed:'Original COLOR and output rows lie behind cue7/8. Frame622/EID14 and return input.color are visible. Later source scroll truncates output name prefixes.', repair:'Magnify the original same-frame table above captions; teal input, red code underline, orange post-step output bracket. Never synthesize hidden names or source numbers.'},
    {id:'vsm-distinct-excerpts', cuts:['vsm-debug-a','vsm-lit','vsm-debug-b'], observed:'Debug-colored wheel regions and lit wheel views use different excerpts, labelled as such. Debug colors are not additional illumination; no page/FPS measurement is shown.'},
    {id:'camera-source-cut', cut:'vsm-camera-path', observed:'Wheel and shadow remain together through cue34. A cut switches to the museum/city view within cue35 by157.517s; it is not one continuous camera path.', supersedes:'Historical native v10 planning phrase different building within the same camera path', repair:'Keep cue33/34 wheel framing and label the later excerpt transition explicitly. Do not infer object/light motion, memory updates or FPS from it.'},
    {id:'smrt-independent-geometry', observed:'Projected blocker, five explicitly illustrative depth samples and SMRT-vs-scene-triangle caveat are visible. Footer clearance still fails in two-line cues; sampled state changes do not approve continuous motion.'}
  ],
  preservedHistory: [
    {execution:base+'first-chapter-review-execution-v10.json', sessionId:49219, exitCode:1, reason:'Clean/18cuts completed, failed caption frame-count guard;10300vs11664frames'},
    {execution:base+'first-chapter-caption-recovery-execution-v11.json', sessionId:6685, exitCode:1, reason:'Boundary test completed; duration-field KeyError preserved in verificationRepairHistory'},
    {execution:base+'first-chapter-caption-recovery-execution-v11.json', sessionId:92510, exitCode:0, reason:'Guarded resume retained completed test and clean; full caption11664frames and decode passed'}
  ],
  allFirstChapterSampledPixelsRead:true,
  firstChapterCaptionClearanceApproved:false,
  allFinalPixelsReviewed:false, allMovingPixelsReviewed:false, causalFlowApproved:false,
  finalMixedAsrApproved:false, wholeEpisode60to40Approved:false, qaApproved:false, collected:false, uploaded:false,
  humanWholeListening:'pending', newTts:0, newGitImages:0
};
fs.writeFileSync(out, JSON.stringify(r,null,2)+'\n');
const cp='production/research/game-lighting-history/checkpoint.json', j=read(cp);
j.episode04FirstChapterDirectPixelReview={path:out,sha256:sha(out),sampledBoardsRead:73,captionClearanceApproved:false,allFinalPixelsReviewed:false,next:'Repair only observed caption/source-label collisions; continuous motion and remaining99 paragraphs still pending'};
j.ownedActiveWork={status:'no-active-owned-media-worker',lastExecution:extractionPath,next:'CPU-only first-chapter scoped framing corrections; preserve completed sources and PCM'};
j.updatedAt=r.recordedAt;fs.writeFileSync(cp,JSON.stringify(j,null,2)+'\n');
console.log(JSON.stringify({record:out,boards:73,failuresRecorded:3,allFinalPixelsReviewed:false}));
