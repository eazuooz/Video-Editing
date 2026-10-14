/* Complete narration records only after the live worker and research return. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const rel = p => path.relative(root, p).replace(/\\/g, '/');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const write = (p, value) => {
  const temp = p + '.tmp-' + process.pid;
  fs.writeFileSync(temp, JSON.stringify(value, null, 2) + '\n');
  fs.renameSync(temp, p);
};
const now = new Date().toISOString();
const generationOnly = process.argv.includes('--generation-only');
const executionPath = path.join(__dirname, 'remaining-tts-execution-v2.json');
const execution = read(executionPath);
if (execution.status !== 'all-remaining-tts-produced-and-decoded' || execution.exitCode !== 0
    || execution.researchPreservationVerified !== true)
  throw Error('Actual successful worker completion required.');
const leasePath = path.join(root, 'shared/output/GPU_HANDOFF.json');
if (!generationOnly && fs.existsSync(leasePath)) throw Error('A GPU handoff is still active; preserve its owner.');
const resumePath = path.join(__dirname, 'research-user-resume-after-all-tts-v2.json');
const resume = read(resumePath);
if (resume.token !== execution.token || resume.priorCompletedMarkersPreserved !== true
    || resume.originalCommandRestored !== true || resume.ownedPauseControlsRemoved !== true
    || (!generationOnly && (resume.actualResearchGpuRunningVerified !== true || resume.researchLogProgressVerified !== true)))
  throw Error('Actual original research GPU/log restoration evidence required.');
if (generationOnly && fs.existsSync(leasePath)) {
  const foreign = read(leasePath);
  if (foreign.token === execution.token || foreign.token !== resume.foreignLease?.token)
    throw Error('Unexpected live lease scope; preserve its owner.');
}
const indexPath = path.join(__dirname, 'narration-review-index.json');
const index = read(indexPath);
if (!index.allFourNarrationsGenerated || index.episodes.length !== 4)
  throw Error('Current four-episode listening index required.');
const first = read(path.join(root, 'projects/game-lighting-history-01/production/tts-repair-completion-v4.json'));
const firstDecode = read(path.join(__dirname, 'episode01-current-wav-verification-v2.json'));
if (firstDecode.exitCode !== 0 || firstDecode.audioSha256 !== first.audio.sha256)
  throw Error('Actual current episode1 whole WAV decode required.');
const previousStates = [];
const episodes = index.episodes.map(episode => {
  const manifestPath = path.join(root, `projects/${episode.slug}/project.json`);
  const manifest = read(manifestPath);
  const timingPath = path.join(root, manifest.tts.outputDir, manifest.tts.filenameStem + '.timing.json');
  const expected = episode.number === 1 ? first.audio.sha256
    : execution.verification.find(v => v.slug === episode.slug)?.audioSha256;
  if (!expected || episode.audioSha256 !== expected || sha(episode.audioPath) !== expected)
    throw Error('Current measured WAV hash differs: ' + episode.slug);
  const timing = read(timingPath);
  if (Math.abs(timing.duration_seconds - episode.durationSeconds) > 1 / 24000)
    throw Error('Current duration differs.');
  const captions = {};
  for (const [language, key] of [['ko', 'captionsKo'], ['en', 'captionsEn']]) {
    const file = path.join(root, manifest.paths[key]);
    if (!fs.existsSync(file)) throw Error('Missing generated captions.');
    captions[language] = {path: rel(file), sha256: sha(file),
      cueCount: [...fs.readFileSync(file, 'utf8').matchAll(/^\d+\s*$/gm)].length,
      wordAligned: false, finalPixelsApproved: false};
  }
  previousStates.push({slug: episode.slug, status: manifest.status,
    productionState: manifest.productionState, narrationProduced: manifest.productionGates.narrationProduced});
  const produced = {path: rel(episode.audioPath), sha256: expected,
    durationSeconds: episode.durationSeconds, sceneCount: episode.sceneCount,
    paragraphPairs: episode.paragraphPairs, timing: {path: rel(timingPath), sha256: sha(timingPath)}, captions};
  return {...episode, audioPath: produced.path, generatedNarration: produced,
    wholeWavDecodeExitCode: episode.number === 1 ? firstDecode.exitCode
      : execution.verification.find(v => v.slug === episode.slug).wholeWavDecode.exitCode,
    currentNarrationApproved: false, humanWholeListeningApproved: false,
    finalMixedAsrApproved: false, finalVideoProduced: false};
});
const completionPath = path.join(__dirname, 'all-tts-completion-v2.json');
const priorCompletion = fs.existsSync(completionPath) ? read(completionPath) : null;
const completion = {schemaVersion: 2, observedAt: now, token: execution.token,
  workerEvidence: rel(executionPath), researchReturnEvidence: rel(resumePath),
  allFourNarrationsGenerated: true, existing01And02Preserved: true,
  allFourWholeWavDecodeExitCodesZero: true,
  episodes, previousProductionStates: priorCompletion?.previousProductionStates ?? previousStates,
  actualResearchGpuRunningVerified: resume.actualResearchGpuRunningVerified === true,
  researchReturnStatus: generationOnly ? 'original-queue-restored-then-foreign-TTS-boundary; actual-GPU-return-pending' : 'actual-original-research-GPU-and-log-progress-verified',
  scope: 'Generated narration and provisional KO/EN captions, not completed videos.',
  currentNarrationApproved: false, humanWholeListeningApproved: false,
  finalMixedAsrApproved: false, finalVideoProduced: false,
  exactWordAlignmentApproved: false, final60to40Measured: false,
  allAnimated25dPixelsReviewed: false, allEncodedPixelsReviewed: false,
  outputCollected: false, uploaded: false, newRasterOrMediaStaged: false};
write(completionPath, completion);
for (const episode of episodes) {
  const p = path.join(root, `projects/${episode.slug}/project.json`);
  const manifest = read(p);
  manifest.status = 'generated-narration-awaiting-voice-and-final-video-review';
  manifest.productionGates.narrationProduced = true;
  // Input reviews were current at synthesis. Production-state metadata has now
  // changed the inventory fingerprint; a later production entry must recheck.
  manifest.productionState.currentDistinctSnapshotAtNarrationGeneration = {
    decisionWasDistinct: priorCompletion?.previousProductionStates?.find(v => v.slug === episode.slug)?.currentDistinct
      ?? manifest.productionGates.currentDistinct,
    freshInventoryRecheckBeforeNextProductionRequired: true,
    reason: 'Generated-audio metadata updated; script text and audio bytes preserved.'};
  manifest.productionGates.currentDistinct = false;
  Object.assign(manifest.productionState, {updatedAt: now, ownedGpuJobs: 0,
    ownedCpuAsrJobs: 0, generatedNarration: episode.generatedNarration,
    measuredNarrationSeconds: episode.durationSeconds, allTtsCompletion: rel(completionPath),
    currentVoiceApproved: false, humanListeningApproved: false,
    researchGpuRestorationEvidence: rel(resumePath)});
  if (episode.number === 1) {
    manifest.productionState.currentVoiceReview = 'Current repaired07 whole/context and preserved12 scene results directly compared; human listening/pronunciation pending.';
    manifest.productionState.currentVoiceDirectReview = 'projects/game-lighting-history-01/production/current-voice-direct-review-v4.json';
  }
  if (episode.number === 2)
    manifest.productionState.currentVoiceDirectReview = 'projects/game-lighting-history-02/production/current-voice-direct-review-v2.json';
  if (episode.number >= 3)
    manifest.productionState.currentVoiceReview = 'Whole/current independent-context ASR and human pronunciation review pending; tail heuristic is not approval.';
  manifest.audio.mixStatus = 'generated-narration-ready-awaiting-current-voice-review-and-final-mix';
  write(p, manifest);
}
const seriesPath = path.join(__dirname, 'series-plan.json');
const series = read(seriesPath);
series.episodes.forEach(episode => {
  const current = episodes.find(e => e.slug === episode.slug);
  if (!current) throw Error('Series episode mismatch.');
  Object.assign(episode, {status: 'generated-narration-awaiting-final-production',
    narrationProduced: true, measuredNarrationSeconds: current.durationSeconds,
    generatedNarration: current.generatedNarration, currentVoiceApproved: false,
    renderProduced: false, timingMeasured: false, finalDurationSeconds: null});
});
Object.assign(series, {updatedAt: now, allFourNarrationsGenerated: true,
  allTtsCompletion: rel(completionPath), ownedGpuJobsRunning: 0,
  activeEpisode: null, productionComplete: false, timingMeasured: false});
write(seriesPath, series);
const checkpointPath = path.join(__dirname, 'checkpoint.json');
const checkpoint = read(checkpointPath);
checkpoint.ownedJobHistory ??= [];
if (checkpoint.ownedRunningJobs?.length) checkpoint.ownedJobHistory.push({recordedAt: now, note: generationOnly ? 'One live03/04 batch actually exited0; original research queue restored, then a preserved foreign TTS request acquired a new boundary; actual research GPU return pending.' : 'One live03/04 batch actually exited0; coordinator restored original research; actual GPU job/log verified.',
  jobs: checkpoint.ownedRunningJobs ?? []});
Object.assign(checkpoint, {updatedAt: now, stage: generationOnly ? 'four-generated-narrations-awaiting-actual-research-GPU-return' : 'four-generated-narrations-and-research-GPU-return',
  status: generationOnly ? 'all-four-TTS-produced-foreign-TTS-boundary-actual-research-GPU-return-pending' : 'all-four-TTS-produced-research-GPU-running-final-video-review-pending',
  ownedRunningJobs: [], ownedJobsRunning: [], ownedActiveWork: [],
  allFourNarrationsGenerated: true, allTtsCompletion: rel(completionPath),
  researchGpuRestorationEvidence: rel(resumePath),
  actualResearchGpuRunningVerified: resume.actualResearchGpuRunningVerified === true,
  next: generationOnly ? 'Observe preserved foreign TTS handoff; verify actual original research GPU/job/log after its natural boundary. Own four generated narrations are complete; do not resynthesize or remove foreign controls.' : 'Continue voice/word alignment, projected animated explanations, actual footage/rights and final media QA using resource scheduling that preserves the restored research. No immediate new GPU job.',
  narrationReviewPage: {...checkpoint.narrationReviewPage, generatedEpisodes: 4, currentNarrationApproved: false},
  spatialParagraphPreparation: {...checkpoint.spatialParagraphPreparation,
    measuredTimingAttached: true, exactWordAlignmentApproved: false,
    measuredPreparationRecord: 'production/research/game-lighting-history/local/spatial-paragraph-measured-preparation-v1.json'},
  finalVideoProduced: false, currentNarrationApproved: false});
checkpoint.checks.duplicateDecision = '03/04 synthesis entered with a current distinct pass after52-project full-content reviews. Generated-audio metadata then changed inventory fingerprints; fresh check required before later production, no script rewrite.';
checkpoint.checks.productionGates = 'Four current generated WAVs and provisional KO/EN verified; voice, exact word timing, final mix, footage/rights, rendered pixels and private delivery remain pending.';
checkpoint.gpuTtsHoldPreserved = 'Historical controls preserved. Completed1623823a token controls removed only by its coordinator; subsequent foreigndf54478a controls preserved and naturally removed by their own coordinator. Actual research return recorded separately.';
write(checkpointPath, checkpoint);
console.log(JSON.stringify({allFourNarrationsGenerated: true,
  episodes: episodes.map(e => ({slug: e.slug, durationSeconds: e.durationSeconds})),
  researchGpuRunning: resume.actualResearchGpuRunningVerified === true, approvedNarrations: 0, completedVideos: 0}));
