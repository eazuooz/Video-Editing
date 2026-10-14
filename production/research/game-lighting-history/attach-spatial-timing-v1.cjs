/* Attach generated narration to preparation; this does not approve voice/pixels. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const input = path.join(__dirname, 'local/spatial-paragraph-plan-v1.json');
const plan = read(input);
const execution = read(path.join(__dirname, 'remaining-tts-execution-v2.json'));
const result = {...plan, createdAt: new Date().toISOString(), sourcePlanSha256: sha(input),
  status: 'generated-narration-timing-attached-preparation-only',
  measuredTimingAttached: false, allGeneratedNarrationsAvailable: false,
  voiceApproved: false, exactWordAlignmentApproved: false,
  actualAnimatedPixelsReviewed: false, finalUseApproved: false,
  timingScope: 'Measured whole WAV and scene boundaries; paragraph allocation is provisional, not word alignment.'};
let available = 0;
for (const episode of result.episodes) {
  const verified = execution.verification.find(v => v.slug === episode.slug);
  const done = execution.completed.find(v => v.slug === episode.slug);
  if (!verified || !done) {
    episode.generatedNarrationAvailable = false;
    continue;
  }
  const source = path.join(root, `projects/${episode.slug}/script/narration.ko.json`);
  if (sha(source) !== episode.scriptSha256) throw Error('Reviewed script changed: ' + episode.slug);
  for (const file of Object.values(done.files)) {
    if (sha(path.join(root, file.path)) !== file.sha256) throw Error('Generated file changed: ' + file.path);
  }
  if (verified.wholeWavDecode.exitCode !== 0 || !verified.generatedNarrationComplete)
    throw Error('Actual generated-audio verification required.');
  const timing = read(path.join(root, done.files['.timing.json'].path));
  const entries = episode.scenes.flatMap(scene => scene.paragraphs.map(p => ({scene, p})));
  if (entries.length !== timing.entries.length) throw Error('Paragraph topology changed.');
  entries.forEach(({scene, p}, i) => {
    const entry = timing.entries[i];
    if (entry.scene_id !== scene.id || entry.text !== p.text) throw Error('Paragraph text changed.');
    p.actualTiming = {start: entry.start, end: entry.end,
      startSample: Math.round(entry.start * verified.sampleRate),
      endSample: Math.round(entry.end * verified.sampleRate),
      mode: 'provisional-paragraph-allocation', exactWordAlignmentApproved: false};
  });
  episode.scenes.forEach(scene => {
    const first = scene.paragraphs[0].actualTiming;
    const last = scene.paragraphs.at(-1).actualTiming;
    scene.generatedAudioSpan = {start: first.start, end: last.end,
      startSample: first.startSample, endSample: last.endSample,
      bodyClassification: 'explanation-model-only; actual footage intervals still separate',
      finalTimelineApproved: false};
  });
  Object.assign(episode, {generatedNarrationAvailable: true,
    generatedAudio: {path: done.files['.wav'].path, sha256: verified.audioSha256,
      durationSeconds: verified.durationSeconds, samples: verified.samples,
      sampleRate: verified.sampleRate, wholeWavDecodeExitCode: 0},
    measuredWholeAndSceneTimingAttached: true, finalTimelineApproved: false});
  available++;
}
if (process.argv.includes('--require-all') && available !== result.episodes.length)
  throw Error('Both verified generated narrations required.');
result.measuredTimingAttached = available === result.episodes.length;
result.allGeneratedNarrationsAvailable = available === result.episodes.length;
const output = path.join(__dirname, 'local/spatial-paragraph-measured-preparation-v1.json');
fs.writeFileSync(output, JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({output, measuredEpisodes: available,
  exactWordAlignmentApproved: false, animatedPixelsReviewed: false, imagesCreated: 0}));
