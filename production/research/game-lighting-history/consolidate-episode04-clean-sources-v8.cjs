// Select verified sources; never render, trim narration, or approve final allocation.
const fs = require('node:fs');
const crypto = require('node:crypto');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const dir = 'production/research/game-lighting-history/local/';
const planPaths = ['episode04-clean-model-inputs-v5', 'episode04-depth-repairs-v6', 'episode04-comparison-clearance-v7'].map(x => dir + x + '/plan.json');
const plans = planPaths.map(read);
const out = 'projects/game-lighting-history-04/production/clean-source-selection-v8.json';
if (fs.existsSync(out)) throw Error('Preserve completed source selection');
const replacement = {'original-18t-2': 2, 'original-18t-6': 1, 'original-18a-5': 1, 'original-conclusion-4': 1};
const jobCache = new Map();
function verifiedJob(plan, job) {
  if (jobCache.has(job.output)) return jobCache.get(job.output);
  const verificationPath = job.execution.replace('.execution.json', '.verification.json');
  const verification = read(verificationPath);
  if (verification.execution.observedExitCode !== 0 || verification.wholeDecodeExitCode !== 0 || verification.allPacketPtsAndDurationsApproved !== true || verification.frames !== job.frames || verification.timeBase !== '1/90000' || verification.ptsStep !== 1500 || sha(job.output) !== verification.media.sha256) throw Error('Verified media changed: ' + job.name);
  const reviewRef = job.sourceSampleReview || plan.firstJobBoundaryReview;
  if (!reviewRef || sha(reviewRef.path) !== reviewRef.sha256) throw Error('Actual direct source review missing');
  const review = read(reviewRef.path);
  if (!review.cleanSourceConfirmed || review.media.sha256 !== verification.media.sha256) throw Error('Review does not match clean source');
  const result = {media: verification.media, verification: {path: verificationPath, sha256: sha(verificationPath)}, review: reviewRef, reviewValue: review};
  jobCache.set(job.output, result);
  return result;
}
const selected = plans[0].scenes.map(original => {
  const index = replacement[original.id] || 0;
  const plan = plans[index], scene = plan.scenes.find(s => s.id === original.id);
  const job = plan.jobs.find(j => j.scenes.some(s => s.id === original.id));
  const span = job.scenes.find(s => s.id === original.id), evidence = verifiedJob(plan, job);
  if (scene.originalPcmSha256 !== original.originalPcmSha256 || scene.frames !== original.frames || JSON.stringify(scene.sourceSamples) !== JSON.stringify(original.sourceSamples) || scene.currentText !== original.currentText || scene.independentEnglishText !== original.independentEnglishText) throw Error('Narration/clock/content changed');
  const findings = evidence.reviewValue.findings;
  if (index === 1 && !findings.acceptedSourceScenes.includes(original.id)) throw Error('Repair scene not accepted');
  if (index === 2 && evidence.reviewValue.sourceSamplePixelsApproved !== true) throw Error('Clearance repair not accepted');
  if (index === 0 && evidence.reviewValue.sourceSamplePixelsApproved === false) {
    // Aggregate failures identify one scoped scene; retain the other reviewed scenes.
    const repairIds = evidence.reviewValue.findings.requiredRepair?.paragraph ? [evidence.reviewValue.findings.requiredRepair.paragraph] : (evidence.reviewValue.findings.repairRequired || []).map(x => x.split(':')[0]);
    if (!repairIds.length || repairIds.includes(original.id) || repairIds.some(id => !replacement[id])) throw Error('Unresolved baseline rejection: ' + original.id);
  }
  return {id: scene.id, chapter: scene.chapter, frames: scene.frames, sourceSamples: scene.sourceSamples, originalPcmSha256: scene.originalPcmSha256, textKo: scene.currentText, textEn: scene.independentEnglishText, stages: scene.stages, cues: scene.cues, wrapper: scene.wrapper, selectedVersion: index === 0 ? 'v5' : index === 1 ? 'v6' : 'v7', media: evidence.media, mediaSpanFrames: [span.fromFrame, span.toFrame], verification: evidence.verification, sourceSampleReview: evidence.review, sourceSamplePixelsApproved: true, fullMovingPixelReviewApproved: false, finalAllocationApproved: false};
});
if (selected.length !== 98 || new Set(selected.map(s => s.id)).size !== 98) throw Error('Expected98 unique explanation sources');
const result = {recordedAt: new Date().toISOString(), scope: '98 complete clean paragraph-source preparations. This source bank is not the retained final explanation duration or final40% allocation.', priorPlans: planPaths.map(p => ({path:p,sha256:sha(p)})), currentAudio: plans[0].currentAudio, currentAssembly: plans[0].currentAssembly, paragraphPairs:111, selected, nativeGuideIds:plans[0].nativeGuideIds, totalSourceFrames:selected.reduce((n,s)=>n+s.frames,0), repairCount:4, baselineVersionsPreserved:true, allSelectedSourceSamplesReviewed:true, allFinalPixelsReviewed:false, finalMixedAsrApproved:false, final60to40Approved:false, outputCollected:false, uploaded:false, newMedia:0, newGitImages:0};
fs.writeFileSync(out, JSON.stringify(result,null,2)+'\n');
const checkpointPath='production/research/game-lighting-history/checkpoint.json';
const c=read(checkpointPath);
c.updatedAt=result.recordedAt;
c.stage='episode04-clean-source-selection-native-interleaving-preparation-v8';
c.cleanSourceSelectionV8={path:out,sha256:sha(out),selectedSources:98,replacements:4,sourcePreparationFrames:result.totalSourceFrames,finalAllocationApproved:false};
c.ownedActiveWork={status:'no-active-owned-media-worker',previous:c.ownedActiveWork,next:'Review native before/action/after and create exact narration-preserving interleaving; then final mix ASR and encoded QA',observedAt:result.recordedAt};
c.nextAction='Use verified v5 sources plus three accepted v6 scenes and one v7 clearance repair. Keep source-bank duration separate from final allocation. Native crop/normal motion, exact causal cut mapping, final60:40, mixed ASR, captions/QA/output/private remain pending.';
fs.writeFileSync(checkpointPath,JSON.stringify(c,null,2)+'\n');
console.log(JSON.stringify({record:out,selected:98,replacements:4,sourceFrames:result.totalSourceFrames,newMedia:0,final:false}));
