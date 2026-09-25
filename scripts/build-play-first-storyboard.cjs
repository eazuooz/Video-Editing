// Build motion-canvas/src/projects/play-first/storyboard.generated.json from the measured narration.
// Inputs: generated timing.ts (scene starts/durations), timing JSON (line starts) and the aligned KO SRT.
// The Odyssey example window is placed so the footage overlaps the line that describes it.
// Usage: node scripts/build-play-first-storyboard.cjs
const fs = require('node:fs'), path = require('node:path');
const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects/play-first/project.json'), 'utf8'));
const exampleSeconds = manifest.editing.exampleSeconds;
const outroSeconds = manifest.editing.outro.seconds;
const timingTs = fs.readFileSync(path.join(root, 'motion-canvas/src/projects/play-first/timing.ts'), 'utf8');
const array = name => JSON.parse(timingTs.match(new RegExp(`${name} = (\\[[^\\]]*\\])`))[1].replace(/,\s*\]/, ']'));
const starts = array('SCENE_STARTS'), durations = array('SCENE_DURATIONS');
const timing = JSON.parse(fs.readFileSync(path.join(root, manifest.paths.narration.replace(/\.wav$/, '.timing.json')), 'utf8'));
const srt = fs.readFileSync(path.join(root, manifest.paths.captionsKo), 'utf8').trim().split(/\r?\n\r?\n/).map(block => {
  const lines = block.split(/\r?\n/);
  const [a, b] = lines[1].split(' --> ').map(t => {
    const [h, m, s] = t.replace(',', '.').split(':').map(Number);
    return h * 3600 + m * 60 + s;
  });
  return {start: a, end: b, text: lines.slice(2).join(' ')};
});
// Line index (within each scene) of the sentence that describes the Odyssey footage.
const exampleLine = {'01': 4, '02': 3, '03': 2, '04': 2, '05': 2};
const lead = 1.0;
const scenes = starts.map((start, i) => {
  const id = String(i + 1).padStart(2, '0');
  const duration = durations[i];
  const lineStarts = timing.entries.filter(e => e.scene_id === id).map(e => +(e.start - start).toFixed(3));
  const wanted = lineStarts[exampleLine[id]] - lead;
  const exampleStart = +Math.min(Math.max(wanted, 1.5), duration - exampleSeconds - 0.25).toFixed(3);
  if (exampleStart < 0) throw Error(`scene ${id} is shorter than the example`);
  const captions = srt.filter(c => c.start >= start - 0.01 && c.start < start + duration - 0.01)
    .map(c => ({start: +(c.start - start).toFixed(3), end: +(Math.min(c.end, start + duration) - start).toFixed(3), text: c.text}));
  return {id, start, duration, lineStarts, exampleLine: exampleLine[id], exampleStart, exampleEnd: +(exampleStart + exampleSeconds).toFixed(3), captions};
});
const body = starts[starts.length - 1] + durations[durations.length - 1];
const out = {generatedAt: new Date().toISOString(), fps: 60, exampleSeconds, outroSeconds,
  bodySeconds: body, totalSeconds: body + outroSeconds, scenes};
fs.writeFileSync(path.join(root, 'motion-canvas/src/projects/play-first/storyboard.generated.json'), JSON.stringify(out, null, 2) + '\n');
for (const s of scenes) console.log(s.id, 'dur', s.duration.toFixed(2), 'ex', s.exampleStart, '-', s.exampleEnd, 'odysseyLine@', s.lineStarts[s.exampleLine], 'cues', s.captions.length);
console.log('body', body.toFixed(3), 'total', (body + outroSeconds).toFixed(3));
