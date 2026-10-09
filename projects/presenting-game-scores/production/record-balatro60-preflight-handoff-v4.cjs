const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const root = path.resolve(__dirname, '../../..');
const base = path.join(__dirname, 'revision-balatro60-v2');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel = p => path.relative(root, p).replaceAll('\\', '/');
const save = (p, value) => {
  const temp = p + '.' + process.pid + '.writing';
  fs.writeFileSync(temp, JSON.stringify(value, null, 2) + '\n');
  fs.renameSync(temp, p);
};
const output = path.join(base, 'preflight-handoff-v4.json');
if (fs.existsSync(output)) throw Error('Read completed handoff; duplicate record refused');
const requestPath = path.join(base, 'request.json');
const request = read(requestPath);
const reviewPath = path.join(base, 'native-actions-sample-direct-review-v3.json');
const review = read(reviewPath);
const playbackPath = path.join(base, 'native-action-playback-observations-v3.json');
const playback = read(playbackPath);
const layoutPath = path.join(base, 'native-credit-layout-observation-v4.json');
const layout = read(layoutPath);
if (review.sampleCount !== 201 || review.boardCount !== 34 || !review.allListedNativePtsSamplesDirectlyRead || review.footageAdopted) throw Error('Native source review scope mismatch');
const endpoints = review.intervals.map(interval => {
  const ending = playback.observations.find(o => o.paused && o.status.startsWith(interval.id + ' | ') && o.time >= interval.draft[1] && o.time < interval.draft[1] + 0.3 && o.rate === 1 && o.muted === true);
  if (!ending) throw Error('Missing actual normal-speed endpoint: ' + interval.id);
  const start = playback.observations.find(o => !o.paused && o.time >= interval.draft[0] && o.time < interval.draft[0] + 0.3 && o.rate === 1 && o.muted === true);
  return { id: interval.id, draft: interval.draft, recordedStart: start || null, recordedEnd: ending, browserOvershootSeconds: ending.time - interval.draft[1], exactBoundsFromNativePtsOnly: true };
});
for (const snapshot of request.baseline.snapshots) {
  if (sha(path.join(root, snapshot.snapshot)) !== snapshot.snapshotSha256) throw Error('Preserved baseline snapshot changed: ' + snapshot.snapshot);
}
const protectedFiles = [
  'projects/presenting-game-scores/script/narration.ko.json',
  'projects/presenting-game-scores/script/narration.en.json',
  'projects/presenting-game-scores/sources/game-candidates.json',
  'projects/presenting-game-scores/production/current-voice-selection-v7.json',
  'projects/presenting-game-scores/production/measured-timeline-candidate-v7.json',
  'projects/presenting-game-scores/production/final-v1/plan.json',
  'projects/presenting-game-scores/production/final-v1/final-pixel-direct-review-v1.json',
  'projects/presenting-game-scores/production/delivery-output.json',
];
const preserved = protectedFiles.map(p => {
  const original = request.baseline.snapshots.find(s => s.path === p);
  const currentSha256 = sha(path.join(root, p));
  if (!original || original.sha256 !== currentSha256) throw Error('Protected baseline production input changed: ' + p);
  return { path: p, sha256: currentSha256, baselineByteIdentical: true };
});
const rightsImage = path.join(root, 'shared/output/presenting-game-scores/revision-balatro60-v2/rights/c1WD4x9Dyg0-credit-condition.png');
const nativeImage = path.join(root, layout.screenshot);
const proposal = path.join(base, 'balanced-edit-proposal-v2.md');
const now = new Date().toISOString();
const nextAction = 'Await the existing user question about one description credit link for this recording. Keep preflight ready; do not adopt footage or create dependent revised narration/TTS until answered. If allowed, inspect final exact source boundaries/caption UI, refresh current distinct review, then selectively revise bilingual commentary and measure both ratios.';
const proof = {
  schemaVersion: 1, slug: request.slug, revision: request.revision, recordedAt: now,
  sourceSamples: { review: rel(reviewPath), sha256: sha(reviewPath), samples: 201, boards: 34, allListedSamplesDirectlyRead: true, allNativeFramesReviewed: false },
  playback: { path: rel(playbackPath), sha256: sha(playbackPath), endpoints, observedEndpointCount: endpoints.length, observedStartCount: endpoints.filter(e => e.recordedStart).length, normalSpeedMutedWindowsExecuted: true, interveningEveryFrameDirectReview: false, continuousWholeWatchingOrListeningApproved: false },
  captionAndCreditPreflight: { path: rel(layoutPath), sha256: sha(layoutPath), screenshot: rel(nativeImage), screenshotSha256: sha(nativeImage), v3WideCreditOverlapObserved: true, v4TargetEndpointCreditClearOfAncientJoker: layout.observedCreditNoLongerCoversAncientJokerAtReviewedEndpoint === true, lowerPlayHandControlsCoveredByPreparedCaptionAtSomeEarlierSamples: true, finalEveryCueFramingApproved: false, fullLicenseCreditStillToPrepare: true },
  conditionalEditProposal: { path: rel(proposal), sha256: sha(proposal), draftBalatroSeconds: 110, planningOnly: true, gameplayTargetBalatro: 0.6, gameplayTargetTetris: 0.4, bodyTargetActual: 0.6, bodyTargetExplanation: 0.4, neitherRatioMeasuredOrApproved: true },
  attribution: {
    sourceVideo: 'https://www.youtube.com/watch?v=c1WD4x9Dyg0',
    recorder: 'Squeaky Whale Gameplay Archive',
    sourceConditionScreenshot: rel(rightsImage), sourceConditionScreenshotSha256: sha(rightsImage),
    requiresVisibleOnscreenCredit: true, requiresDescriptionLink: true,
    proposedDescriptionLine: '플레이 녹화: Squeaky Whale Gameplay Archive — https://www.youtube.com/channel/UCoMF_6EsJYSq8vWG8zqRvtA',
    existingAsyncQuestionAnswer: 'pending', userOmitPublicSourceBlockExceptionApproved: false,
    assumeConsentFromElapsedTime: false, recordingAdopted: false, finalPublicRightsApproved: false,
  },
  preserved, baselineVideoId: 'oDYJlcv2Dqk', baselineDeleted: false,
  revisionGates: { sourceAdoption: false, revisedNarration: false, revisedTts: false, measuredTiming: false, gameplayRatio: false, bodyRatio: false, finalMixedAsr: false, pair: false, allFinalPixels: false, qa: false, collected: false, privateSaved: false, gitDelivered: false },
  actualRevisionVideoId: null, newImagesGitAdded: 0, researchProcessChanges: 0,
  completedSourceWorkersExpectedRunning: false, nextAction,
};
save(output, proof);
request.recordedAt = now;
request.stage = 'native-source-and-conditional-balanced-edit-preflight-awaiting-credit-exception';
request.preflightHandoff = rel(output);
request.attributionUserAnswer = 'pending';
request.nextAction = nextAction;
save(requestPath, request);
const checkpointPath = path.join(__dirname, 'latest-checkpoint.json');
const checkpoint = read(checkpointPath);
checkpoint.recordedAt = now;
checkpoint.stage = 'balatro60-tetris40-revision-awaiting-description-credit-exception';
checkpoint.revisionPreflightHandoff = rel(output);
checkpoint.revisionNativePlaybackReview = rel(playbackPath);
checkpoint.nextAction = nextAction;
checkpoint.currentApprovalScope = 'Top-level true media approvals describe preserved final-v1 only. Active revisionCheckpoints remain unapproved; no revised media, upload or Git delivery exists.';
save(checkpointPath, checkpoint);
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const queue = read(queuePath);
const item = queue.items.find(i => i.slug === request.slug);
if (!item) throw Error('Missing queue item');
item.revisionPreflightHandoff = rel(output);
item.revisionNativePlaybackReview = rel(playbackPath);
item.nextAction = nextAction;
item.revisionAttributionException = 'awaiting-existing-user-question-answer';
queue.updatedAt = now;
queue.lastProgressAt = now;
save(queuePath, queue);
console.log(JSON.stringify({ proof: rel(output), nativeSamples: 201, boards: 34, observedEndpoints: endpoints.length, observedStarts: endpoints.filter(e => e.recordedStart).length, draftBalatroSeconds: 110, adoptedSeconds: 0, pending: 'description-credit-exception-user-answer', finalGatesApproved: false, imagesGitAdded: 0, researchProcessChanges: 0 }));
