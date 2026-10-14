const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write = (p,v) => fs.writeFileSync(path.join(root,p),JSON.stringify(v,null,2)+'\n');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const planPath = 'production/research/game-lighting-history/black-lookdev-plan-v2.json';
const reviewPath = 'production/research/game-lighting-history/black-lookdev-review-v2.json';
if (fs.existsSync(path.join(root,reviewPath))) throw Error('Recorded direct review preserved.');
const plan = read(planPath);
const extractionPath = 'projects/game-lighting-history-01/production/local/black-lookdev-v2/qa/extraction.json';
const extraction = read(extractionPath);
if (extraction.boards.length !== 6 || extraction.frames.length !== 36 || extraction.wholeDecode.exitCode !== 0)
  throw Error('Missing actual proof media/decode/frame evidence.');
const revisionPath = 'production/research/game-lighting-history/black-style-revision-v2.json';
const revision = read(revisionPath);
for (const item of revision.before) for (const field of ['narration','koScript','enScript'])
  if (sha(item[field].path) !== item[field].sha256) throw Error(`Preserved input changed: ${item.slug} ${field}`);
const findings = [
  ['store','Projected three storage planes and prism remain separated; light moves while stored-grid state remains visible. White labels and yellow heading readable.'],
  ['visibility','Overlapping triangles, depth plane and moving teal arrow stay distinct; no text/caption overlap in sampled poses.'],
  ['sector','Actor crosses projected sector boundary with occlusion; white sector labels and dark actor eyes readable against muted faces.'],
  ['bake','Light ray, blocker, baked-grid plane and separate texture plane readable across the three poses.'],
  ['filter','Three mip planes, sampling points and result disc distinguishable; white weights and caption remain separate.'],
  ['tile','Triangle bins, layered on-chip stack and output plane visibly separated; moving triangle path readable.'],
  ['volume','Projected receiver plane and blocker remain visible on black; light changes position. Full shadow-volume algorithm coverage is outside this first-paragraph proof.'],
  ['normal','Red/green/teal axes, white normal and material disc remain distinguishable; disc changes with the normal while geometry silhouette stays fixed.'],
  ['depth','Blocker prism, receiver sample, stored light-depth grid and ray have separate colors; comparison text readable.'],
  ['cascade','Near/middle/far projected frustum volumes and arrow readable; muted far planes remain visible. Sample values are diagram examples, not measured engine settings.'],
  ['pipeline','Forward/Deferred branches, spatial buffer stack and source rays readable. This first paragraph starts with zero-valued terms; later algorithm steps need their own full review.'],
  ['ao','Projected surface and occluder, local sample cloud and teal rays distinguishable; caption does not cover the sample cloud.'],
];
const now = new Date().toISOString();
const cases = plan.cases.map((c,i) => {
  if (findings[i][0] !== c.model) throw Error('Case-order mismatch');
  return {...c,frames:extraction.frames.filter(f=>f.caseIndex===i),directlyViewed:true,finding:findings[i][1]};
});
const sources = [
  'motion-canvas/src/styles/research-dark.ts',
  'motion-canvas/src/projects/game-lighting-history-shared/depth-space.tsx',
  'motion-canvas/src/projects/game-lighting-history-01/final/black-models-v2.tsx',
  'motion-canvas/src/projects/game-lighting-history-01/black-lookdev-v2/runtime.tsx',
  'motion-canvas/src/projects/game-lighting-history-01/black-lookdev-v2/project.ts',
  'motion-canvas/vite.game-lighting-history.black-lookdev-v2.config.ts',
  'projects/game-lighting-history-01/production/animation-storyboard-v3.json',
].map(p=>({path:p,sha256:sha(p)}));
const guiPath = 'projects/game-lighting-history-01/production/local/black-lookdev-v2/qa/gui-completed.png';
const record = {schemaVersion:2,reviewedAt:now,styleId:'research-black-v1',scope:'12 first-paragraph model color/geometry motion proofs; 3 sampled poses each',
  video:extraction.video,plannedFrames:extraction.plannedFrames,observedFrames:extraction.observedFrames,
  endpointDifference:extraction.endpointDifference,endpointNote:extraction.endpointNote,
  wholeDecodeExitCode:extraction.wholeDecode.exitCode,extraction:extractionPath,
  gui:{url:'http://127.0.0.1:9265/',tabId:'15',exporter:'Video (FFmpeg)',resolution:[1920,1080],renderFps:60,previewFps:30,
    completedRenderButtonObserved:true,screenshot:{path:guiPath,sha256:sha(guiPath)}},
  producer:{ffmpegPid:23960,parentPid:44808,creationDate:'2026-10-09T20:45:24.314486+09:00',
    endedObserved:true,exitCodeDirectlyObserved:false,encodedFileAndWholeDecodeObserved:true,cpuThreads:2},
  previewServer:{pid:44808,parentPid:68544,creationDate:'2026-10-09T20:44:23.844563+09:00',sessionId:37569,
    command:'node node_modules/vite/bin/vite.js --config vite.game-lighting-history.black-lookdev-v2.config.ts',cwd:'D:/Github/Video-Editing/motion-canvas',aliveObserved:true},
  cases,boards:extraction.boards.map(b=>({...b,directlyViewed:true})),sources,
  firstExtractionFailure:{exitCode:1,reason:'Bundled FFmpeg does not support fps_mode; no frames produced. Corrected to vsync 0 before one actual extraction.'},
  preservation:{allFourCurrentNarrationAndKoEnHashesMatch:true,newRasterOrMediaStaged:false,allQaImagesLocalOnly:true,
    researchObservedAt:'2026-10-09T20:53:08+09:00',researchQueuePid:17136,researchChildPid:67084,
    researchJob:'infer_test_normal_p114_44',completedResearchJobs:511,totalResearchJobs:1088,researchControlsChanged:false},
  prototypePaletteAndSampledSpatialPixelsApproved:true,allCurrentNarrationTimedExplanationPixelsApproved:false,
  allFinalEncodedCaptionPixelsApproved:false,finalVideoProduced:false,uploaded:false,
  next:'Apply this reviewed palette to all narration-timed explanation models; review every paragraph/cue, current voice and native footage, then exact final body timing and encoded masters.'};
write(reviewPath,record);
plan.pixelsReviewed=true;plan.reviewScope=record.scope;plan.review=reviewPath;plan.finalVideoProduced=false;write(planPath,plan);
revision.prototypeProof={review:reviewPath,models:12,sampledFrames:36,boards:6,paletteAndSampledSpatialPixelsApproved:true};
revision.currentBlackAnimatedPixelsReviewed=false;revision.finalVideoProduced=false;write(revisionPath,revision);
const cpPath='production/research/game-lighting-history/checkpoint.json';const cp=read(cpPath);
cp.updatedAt=now;cp.blackLookdevReview=reviewPath;cp.blackLookdev={models:12,seconds:Number(extraction.video.duration),
  observedFrames:extraction.observedFrames,sampledFrames:36,boards:6,prototypeReviewed:true,allFinalPixelsReviewed:false,
  producerEnded:true,previewServer:record.previewServer};
cp.explanationPaletteRevision.blackAnimatedPixelsReviewed=false;
cp.next=record.next;write(cpPath,cp);
for(const item of revision.before){
  const p=`projects/${item.slug}/project.json`;const manifest=read(p);
  manifest.productionState.explanationPaletteRevision.prototypeReview=reviewPath;
  manifest.productionState.explanationPaletteRevision.blackPixelsApproved=false;write(p,manifest);
}
console.log(JSON.stringify({prototypeModelsReviewed:12,sampledFrames:36,wholeDecodeExitCode:0,
  preservedVoiceAndScripts:4,allFinalPixelsApproved:false,finalVideoProduced:false}));
