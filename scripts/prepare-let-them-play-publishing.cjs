// Export upload-only assets. Never change picture, audio, timing, or original SRTs.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const resolve = p => path.join(root, p);
const read = p => fs.readFileSync(resolve(p), 'utf8').replace(/^\uFEFF/, '');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(resolve(p))).digest('hex');
const manifest = JSON.parse(read('projects/let-them-play/project.json'));
const timeline = JSON.parse(read(manifest.paths.timeline));
const sourcePath = 'projects/let-them-play/script/captions.upload.en.json';
const translation = JSON.parse(read(sourcePath));
const output = 'projects/let-them-play/publishing';

function parseTimestamp(s) {
  const m = /^(\d{2}):([0-5]\d):([0-5]\d),(\d{3})$/.exec(s);
  assert(m, `Bad timestamp: ${s}`);
  return (+m[1] * 3600 + +m[2] * 60 + +m[3]) * 1000 + +m[4];
}
function parseSrt(text) {
  return text.trim().split(/\r?\n\s*\r?\n/).map((block, i) => {
    const [id, time, ...lines] = block.split(/\r?\n/);
    assert.equal(+id, i + 1, 'Nonsequential SRT');
    const bounds = time.split(' --> ');
    assert.equal(bounds.length, 2);
    assert(lines.length > 0 && lines.length <= 2 && lines.every(s => s.trim()), `Empty/overlong cue ${id}`);
    return {id: +id, time, start: parseTimestamp(bounds[0]), end: parseTimestamp(bounds[1]), lines};
  });
}
function wrap(text) {
  if (text.length <= 46) return text;
  const words = text.split(' '), candidates = [];
  for (let i = 1; i < words.length; i++) {
    const a = words.slice(0, i).join(' '), b = words.slice(i).join(' ');
    if (a.length <= 46 && b.length <= 46) {
      const score = Math.abs(a.length - b.length) - (/[.,?!;:]$/.test(a) ? 10 : 0);
      candidates.push({text: a + '\n' + b, score});
    }
  }
  assert(candidates.length, `Cannot fit two 46-character lines: ${text}`);
  return candidates.sort((a, b) => a.score - b.score)[0].text;
}

const protectedPaths = [manifest.paths.videoClean, manifest.paths.audioMix, manifest.paths.editorAudioMix,
  manifest.paths.captionsKo, manifest.paths.captionsEn, manifest.paths.timeline];
const protectedBefore = Object.fromEntries(protectedPaths.map(p => [p, sha(p)]));
assert.equal(sha(manifest.paths.captionsKo), translation.koreanSourceSha256,
  'Korean source changed: review every cue translation before exporting again.');
const koText = read(manifest.paths.captionsKo), ko = parseSrt(koText);
const script = JSON.parse(read(manifest.paths.script));
const normalize = s => s.replace(/\s+/g, '');
assert.equal(normalize(ko.map(c => c.lines.join(' ')).join(' ')),
  normalize(script.scenes.flatMap(s => s.lines).join(' ')), 'Korean subtitles differ from narration script');
assert.equal(translation.cues.length, ko.length);
const metrics = [];
const enText = ko.map((c, i) => {
  const tr = translation.cues[i];
  assert.equal(tr.id, c.id);
  assert(c.start >= (i ? ko[i - 1].end : 0) && c.end > c.start);
  assert(c.end <= timeline.totalFrames / timeline.fps * 1000);
  assert.equal(tr.text, tr.text.trim());
  assert(!/[\r\n\uFFFD]/.test(tr.text));
  const cps = tr.text.length / ((c.end - c.start) / 1000);
  assert(cps <= 24, `English cue ${c.id} too fast: ${cps.toFixed(2)} characters/sec`);
  metrics.push({id: c.id, charactersPerSecond: +cps.toFixed(2)});
  return `${c.id}\n${c.time}\n${wrap(tr.text)}`;
}).join('\n\n') + '\n';
const en = parseSrt(enText);
assert(ko.every((c, i) => c.time === en[i].time));

const probe = spawnSync('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', resolve(manifest.paths.videoClean)],
  {encoding: 'utf8', windowsHide: true});
assert.equal(probe.status, 0, probe.stderr);
const media = JSON.parse(probe.stdout), picture = media.streams.find(s => s.codec_type === 'video');
assert.equal(+picture.nb_frames, timeline.totalFrames);
assert.equal(picture.r_frame_rate, `${timeline.fps}/1`);
assert(Math.abs(+media.format.duration - timeline.totalFrames / timeline.fps) < .05);

// Markdown files are the publishing source; plain text exports are safe to paste.
const files = new Map([[`${output}/subtitles/let-them-play.ko.srt`, fs.readFileSync(resolve(manifest.paths.captionsKo))],
  [`${output}/subtitles/let-them-play.en.srt`, enText]]);
for (const [language, source, titleHeading, descHeading] of [
  ['ko', manifest.paths.publishingKo, '제목', '설명'],
  ['en', manifest.paths.publishingEn, 'Title', 'Description'],
]) {
  const md = read(source).replace(/\r\n/g, '\n');
  const title = md.match(new RegExp(`^## ${titleHeading}\\n+([^\\n]+)`, 'm'))?.[1];
  assert(title && title.length <= 100, 'Missing or too long title');
  const separator = `## ${descHeading}\n`;
  assert.equal(md.split(separator).length, 2);
  const description = md.split(separator)[1].trim().replace(/^## /gm, '');
  assert(description.length < 5000, 'Description exceeds 5000 characters');
  assert(description.includes(manifest.audio.backgroundMusic.attribution), 'Missing music credit');
  const chapters = [...description.matchAll(/^(\d{2}):(\d{2}) /gm)].map(m => +m[1] * 60 + +m[2]);
  assert.deepEqual(chapters, timeline.scenes.map(s => Math.floor(s.startFrame / timeline.fps)), 'Chapter timings changed');
  files.set(`${output}/title.${language}.txt`, title + '\n');
  files.set(`${output}/description.${language}.txt`, description + '\n');
}
for (const [p, data] of files) {
  fs.mkdirSync(path.dirname(resolve(p)), {recursive: true});
  fs.writeFileSync(resolve(p), data);
}
assert(ko.every((c, i) => parseSrt(read(`${output}/subtitles/let-them-play.en.srt`))[i].time === c.time));
assert.equal(sha(`${output}/subtitles/let-them-play.ko.srt`), sha(manifest.paths.captionsKo));
for (const p of protectedPaths) assert.equal(sha(p), protectedBefore[p], `Protected input changed: ${p}`);
const report = {date: new Date().toISOString(), sourcePath, translationRevision: translation.revision,
  video: manifest.paths.videoClean, frames: timeline.totalFrames, seconds: timeline.totalFrames / timeline.fps,
  koreanCues: ko.length, englishCues: en.length, identicalCueTimes: true, lastCue: ko.at(-1).time,
  koreanTextMatchesScript: true, englishMaxLines: 2, englishMaxLineCharacters: 46,
  englishPeakCharactersPerSecond: Math.max(...metrics.map(m => m.charactersPerSecond)),
  englishTranslationReview: 'Cue-by-cue translation reviewed against Korean; no English audio generated.',
  protectedInputsUnchanged: true, protectedBefore, files: Object.fromEntries([...files.keys()].map(p => [p, sha(p)])),
  humanFullListeningApproval: manifest.audio.humanListeningApproval};
fs.writeFileSync(resolve(`${output}/upload-validation.json`), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({status: 'PASS', frames: report.frames, seconds: report.seconds,
  ko: ko.length, en: en.length, sameTimes: true, maxEnglishCps: report.englishPeakCharactersPerSecond,
  output, protectedInputsUnchanged: true}, null, 2));
