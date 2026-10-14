const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../..');
const target = path.join(root, 'projects/game-lighting-history-04/sources/game-candidates.json');
const evidence = path.join(root, 'production/research/game-lighting-history/episode04-editor-browser-observations-v2.json');
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const previousSha = '01bb2cb33e1651c9a512e54dcb1c01d76544e43459dac07f275b478eb2734152';
if (hash(target) !== previousSha || fs.existsSync(evidence)) throw Error('Preserve current evidence; input changed or revision exists');
const data = JSON.parse(fs.readFileSync(target, 'utf8'));
const now = new Date().toISOString();
const commonPending = {nativeAcquired:false, fullMotionReviewed:false, rightsApproved:false, recentUseCheckPassed:false, finalUseApproved:false};
const virtual = data.candidates.find(x => x.id === 'inGlMVhYB1s');
if (!virtual || data.candidates.some(x => x.id === 'eiT2GlSeSeU')) throw Error('Unexpected candidate inventory');
const virtualSamples = [
  {approxSeconds:2440, visibleRole:'Actual HillsideSample editor viewport with colored clipmap/debug bands over the scene; conference border and presenter require exclusion', visibleAction:'Clipmap visualization separates colored regions around the camera; camera changes must be distinguished from setting changes.'},
  {approxSeconds:2466, visibleRole:'Actual editor shadow view and console', visibleAction:'Ferris-wheel shadow and console setting shown; native continuous before/action/after still pending.'},
  {approxSeconds:2486, visibleRole:'Actual editor ferris-wheel shadow state', visibleAction:'Compare changing versus static parts only after native motion review; no exact invalidation-rate measurement approved.'},
  {approxSeconds:2556.873387, visibleRole:'HillsideSample LV_Exterior and Render Resource Viewer', visibleAction:'Shadow.Virtual.PhysicalPagePool is selected as Texture512MB, Resident|UAV. Console autocomplete r.shadow.virtual.max is visible; no applied2048 value in this sampled frame.', sourceOnlyTotals:{resourceCount:43074, resourceSizeMB:8743}},
  {approxSeconds:2576.873387, visibleRole:'Editor plus Render Resource Viewer after the page-budget change', visibleAction:'Shadow.Virtual.PhysicalPagePool reads256MB; associated HZB pool reads42MB. The source table totals are43197 resources/8379MB. These are source-scene values, not our GPU or a whole-frame performance measurement.'},
  {approxSeconds:2611.873387, visibleRole:'Editor console and selected physical-page-pool row', visibleAction:'r.Shadow.Virtual.Cache.StaticSeparate autocomplete/command name is visible while selected pool remains256MB. The value0 is not directly visible in this sample.'},
  {approxSeconds:2616.873387, visibleRole:'Editor and refreshed resource table', visibleAction:'Shadow.Virtual.PhysicalPagePool reads128MB, Resident|UAV; total43202 resources/8250MB. Do not derive a frame-time ratio or claim every scene retains identical quality.'},
  {approxSeconds:2631.873387, visibleRole:'Same editor resource table', visibleAction:'Selected Shadow.Virtual.PhysicalPagePool remains128MB. Camera/cloud details can differ; this is a resource-size observation.'}
];
virtual.observedWebSamples.push(...virtualSamples);
virtual.selectionStatus = 'Actual editor/debug/resource motion located; partial browser samples only, native acquisition and full action review pending';
virtual.candidateSearchWindows = [[2430,2500],[2530,2590],[2590,2632]];
virtual.viewerFocus = 'Track the shadow/debug view, changed console control and exact Shadow.Virtual.PhysicalPagePool row. Compare virtual addressing, allocated storage and cache reuse separately.';
virtual.diagramConnection = 'Keep the original16virtual/5allocated illustrative diagram; connect page/cache storage to the observed512→256→128MB source resource table without equating illustrative page counts to actual counts.';
virtual.insertionPoint = '18v after virtual addressing/page allocation and cache explanations;22r/resource-size inspection. Exact nonrepeated native intervals and subtitles pending.';
virtual.excluded = ['Conference title/slides including1741 and2251 samples', 'Publisher confetti border and presenter inset', 'Inferring overall GPU memory/frame-time/quality from one selected resource', 'Inferring unobserved command values from transcripts alone'];
virtual.overlayPlanPrepared = {status:'prepared-only', anchor:'Actual selected physical-page-pool row and matching console name in editor pixels', motion:'Narration-timed colored outline/pointer follows the row during selection/refresh; keep title/caption bottom fixed', noWorldMeasurement:true, noFreezeForActualQuota:true, finalPixelsReviewed:false};
virtual.transcriptNote = 'Official transcript describes4096→2048 and disabling separate static cache, but seek samples do not expose every applied value. Verify the complete native command/action before writing those value-dependent guide claims.';
Object.assign(virtual, commonPending);
const renderDoc = {
  id:'eiT2GlSeSeU', url:'https://www.youtube.com/watch?v=eiT2GlSeSeU',
  title:'DirectX12 ImGui 초기화·렌더링 | RenderDoc 그래픽 디버깅',
  publisher:'얌얌코딩 (게임 개발)', publisherEvidence:'CUA YouTube page showed the channel identity and Analytics/Edit controls on the existing public video; no settings changed.',
  chapters:['18a','22r','22rb'], engineScope:'Existing recorded DirectX12/ImGui rendering and RenderDoc frame inspection. It demonstrates inspection method, not Unreal-specific GBuffer/GI/shadow/history passes.',
  uiDurationSeconds:731, uiDurationRoundingNote:'UI displayed12:11/12:12 across states; exact native duration pending.',
  transcriptScope:'Full exported Korean automatic transcript read. The capture section begins around8:26; vertex/pixel shader inspection around9:40–11:03.',
  candidateSearchWindows:[[526,574],[594,659]],
  observedWebSamples:[
    {approxSeconds:542, visibleAction:'Frame capture opened with event browser and captured frame.'},
    {approxSeconds:552, visibleAction:'Clear-render-target event and render-target state; not a lighting-algorithm comparison.'},
    {approxSeconds:567.037, visibleAction:'RenderDocv1.38, Frame#622. EID11ClearRenderTargetView then selectedEID14DrawInstanced(3,1) shows the colored triangle on blue. Subsequent EID26/29/32DrawIndexedInstanced and EID35Present are listed.', resource:'SwapchainImage270,1600×900,1mip,R8G8B8A8_UNORM'},
    {approxSeconds:572, visibleAction:'Later command-list output sampled as a dark rectangle. Do not assert the colored triangle is still visible underneath GUI from this sample.'},
    {approxSeconds:632.037, visibleAction:'Triangle texture/event14; Pixel History(0,0) shows the clear event only. This is not an interior triangle fragment history.'},
    {approxSeconds:647.037, visibleAction:'PS debug return input.color line highlighted before execution. SV_Position797.50,265.50,0,1; COLOR0.96125,0.01312,0.02562,1; return/target initially zero.'},
    {approxSeconds:652.037873, visibleAction:'After the shader step, SV_Target and main_return both read0.96125,0.01312,0.02562,1, matching COLOR in this pass-through shader.'}
  ],
  viewerFocus:'Follow one selected draw to its output, then follow COLOR input through return input.color to SV_Target. Inspect dimensions/format/mips before interpreting a resource.',
  diagramConnection:'Projected input→selected command→shader→output layers; illustrative barycentric calculation remains a separate explanation rather than a measured value from this capture.',
  insertionPoint:'22r after resource-format introduction and22rb event/input/output trace, using distinct continuous excerpts after native review.',
  excluded:['Audio as narration', 'Source annotation toolbar if it obscures code or variables', 'Assuming GBuffer/shadow/GI/history events not shown', 'Using capture timing as normal GPU benchmark', 'Treating this existing channel clip as a newly generated playable quota substitute'],
  overlayPlanPrepared:{status:'prepared-only', anchor:'Observed COLOR input row, return input.color line and SV_Target result row', motion:'Narrated orange focus advances with the source shader step; teal connection links matching values while source action remains visible', noUnmeasuredWorldVector:true, noFreezeForActualQuota:true, finalPixelsReviewed:false},
  browserPlaybackNote:'Playback covered roughly562.492–632.037 with only several directly inspected samples. This is not full continuous motion approval.',
  rightsNote:'Existing channel identity observed; verify original asset/music/rights records before final-use approval.',
  ...commonPending
};
data.candidates.push(renderDoc);
Object.assign(data.candidateReview, {reviewedAt:now, stage:'actual-editor-actions-located-partial-browser-review', sourceObservationEvidence:path.relative(root,evidence).replaceAll('\\','/'),
  newImagesCreated:0, actualFootageSecondsApproved:0, allNativePixelsReviewed:false,
  singleActiveCpuJob:'episode03 current mixed ASR v15; no episode04 acquisition/render started',
  remainingCoverage:['Full native action/camera/UI comparison for all candidates','Temporal-upscaling matched comparisons','Visibility-buffer source implementation inspection beyond the existing triangle capture','Modern mobile-deferred conditions','Actual post-processing controls','Current source rights and recent-use review']});
const record = {reviewedAt:now, priorCandidateFileSha256:previousSha, method:'CUA screenshots/DOM/read-only video timing plus directly read source transcript; no browser hidden state or external settings mutation',
  virtualSamples, renderDoc, savedScreenshotFiles:[], newImagesCreated:0, nativeAcquisitionStarted:false, allNativePixelsReviewed:false, nativeSelectionApproved:false, finalUseApproved:false,
  wholeExistingNarrationPreserved:true, currentMixedAsrApproved:false, privateUploaded:false,
  next:'Complete current episode03 CPU ASR review first; then single native acquisition and continuous interval/crop/overlay review before episode04 guide synthesis.'};
fs.writeFileSync(evidence, JSON.stringify(record,null,2)+'\n');
fs.writeFileSync(target, JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify({candidates:data.candidates.length, candidateSha256:hash(target), evidenceSha256:hash(evidence), approvedActualSeconds:0, newMedia:0, newImages:0}));
