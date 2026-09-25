// Mix play-first: narration (-16 LUFS target, unchanged take) + quiet Odyssey source sound (-23 LUFS)
// + continuous approved BGM (-28 LUFS, -3 dB under game sound, runs through the 10s membership outro).
// Without an approved track it writes an explicit no-BGM review mix only (never a final).
// Usage: node scripts/mix-play-first-audio.cjs
const fs = require('node:fs'), path = require('node:path'), {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects/play-first/project.json'), 'utf8'));
const board = JSON.parse(fs.readFileSync(path.join(root, 'motion-canvas/src/projects/play-first/storyboard.generated.json'), 'utf8'));
const A = manifest.audio;
const music = A.backgroundMusic;
const withBgm = music.approvalStatus === 'approved' && music.file;
const assets = path.join(root, 'motion-canvas/src/projects/play-first/assets');
const outStem = withBgm ? 'final-mix' : 'review-mix-nobgm';
const total = board.totalSeconds;

const run = (args) => {
  const r = spawnSync('ffmpeg', args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024});
  if (r.status !== 0) throw Error(`ffmpeg failed: ${(r.stderr || '').slice(-3000)}`);
  return r.stderr;
};
const loudness = (file, extra = []) => {
  const log = run(['-hide_banner', '-nostats', ...extra, '-i', file, '-af', 'loudnorm=print_format=json', '-f', 'null', '-']);
  const start = log.lastIndexOf('{');
  return Number(JSON.parse(log.slice(start, log.indexOf('}', start) + 1)).input_i);
};
const narration = path.join(root, manifest.paths.narration);
const narrationGain = A.narrationTargetLufs - loudness(narration);

const inputs = ['-i', narration];
const filters = [`[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=${narrationGain.toFixed(3)}dB,apad=whole_dur=${total}[nar]`];
const gameLabels = [];
const windows = [];
board.scenes.forEach((s, i) => {
  const clip = path.join(assets, `broll/scene${s.id}.mp4`);
  const gain = A.gameAudioTargetLufs - loudness(clip);
  const at = s.start + s.exampleStart;
  windows.push([at, at + board.exampleSeconds]);
  inputs.push('-i', clip);
  const idx = i + 1;
  filters.push(`[${idx}:a]aresample=48000,aformat=channel_layouts=stereo,volume=${gain.toFixed(3)}dB,` +
    `afade=t=in:d=0.12,afade=t=out:st=${(board.exampleSeconds - 0.3).toFixed(3)}:d=0.3,` +
    `adelay=${Math.round(at * 1000)}:all=1,apad=whole_dur=${total}[g${i}]`);
  gameLabels.push(`[g${i}]`);
});
filters.push(`${gameLabels.join('')}amix=inputs=${gameLabels.length}:normalize=0:duration=longest[game]`);
let bgLabel = '[game]';
if (withBgm) {
  const file = path.join(root, music.file);
  const bgmIdx = board.scenes.length + 1;
  inputs.push('-stream_loop', '-1', '-i', file);
  const gain = A.bgmTargetLufs - loudness(file);
  // Smooth -3 dB dip (0.45s ramps) only while example source sound plays.
  const ramp = windows.map(([a, b]) => `clip(min((t-${(a - 0.45).toFixed(3)})/0.45,(${(b + 0.45).toFixed(3)}-t)/0.45),0,1)`).join('+');
  filters.push(`[${bgmIdx}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:${total},asetpts=PTS-STARTPTS,` +
    `volume=${gain.toFixed(3)}dB,volume='pow(10,${A.bgmDuringGameplayDb}/20*min(1,${ramp}))':eval=frame,` +
    `afade=t=in:d=0.45,afade=t=out:st=${(total - 0.45).toFixed(3)}:d=0.45[bgm]`);
  filters.push(`[game][bgm]amix=inputs=2:normalize=0:duration=longest[bg]`);
  bgLabel = '[bg]';
}
filters.push(`[nar]asplit=2[nar1][key]`);
filters.push(`${bgLabel}[key]sidechaincompress=threshold=${A.duckingThreshold}:ratio=${A.duckingRatio}:attack=15:release=280:makeup=1[ducked]`);
filters.push(`[nar1][ducked]amix=inputs=2:normalize=0:duration=longest,atrim=0:${total},alimiter=limit=0.8:level=false[out]`);

const wav = path.join(assets, `${outStem}.wav`);
run(['-hide_banner', '-v', 'error', '-y', ...inputs, '-filter_complex', filters.join(';'), '-map', '[out]', '-ar', '48000', '-c:a', 'pcm_s16le', wav]);
const m4a = path.join(assets, `${outStem}.m4a`);
run(['-hide_banner', '-v', 'error', '-y', '-i', wav, '-c:a', 'aac', '-b:a', '192k', m4a]);
const log = run(['-hide_banner', '-nostats', '-i', m4a, '-af', 'ebur128=peak=true', '-f', 'null', '-']);
const integrated = Number(log.match(/I:\s+(-?[\d.]+) LUFS/g).pop().match(/-?[\d.]+/)[0]);
const peak = Number(log.match(/Peak:\s+(-?[\d.]+) dBFS/g).pop().match(/-?[\d.]+/)[0]);
const report = {createdAt: new Date().toISOString(), kind: withBgm ? 'final-mix' : 'review-no-bgm (music approval pending; not publishable)',
  wav: path.relative(root, wav).replaceAll('\\', '/'), m4a: path.relative(root, m4a).replaceAll('\\', '/'), totalSeconds: total,
  narrationGainDb: +narrationGain.toFixed(2), exampleWindows: windows.map(w => w.map(v => +v.toFixed(3))),
  bgm: withBgm ? music.title : null, integratedLufs: integrated, truePeakDbtp: peak};
fs.writeFileSync(path.join(root, 'projects/play-first/audio', `${outStem}.report.json`), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
