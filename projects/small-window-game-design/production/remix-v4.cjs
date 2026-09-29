// v4 audio fix (2026-09-29): place each scene's game audio exactly at its gameplay window (silent under diagrams),
// game audio at 80% of the v3 level, BGM replaced with Nimbus — Eveningland (YouTube Audio Library).
// v3 bug: game-XX.wav files are only gameSeconds long and were concatenated back-to-back, so game sound drifted
// into the diagram sections. Picture and captions are unchanged; video streams are copied from the v3 renders.
// Usage: node projects/small-window-game-design/production/remix-v4.cjs build | verify | activate
const fs = require('node:fs'), path = require('node:path'), {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..'), work = path.join(__dirname, 'mix-v4');
const abs = p => path.join(root, p), rel = p => path.relative(root, p).replaceAll('\\', '/');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const write = (p, v) => { fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, typeof v === 'string' ? v : JSON.stringify(v, null, 2) + '\n'); };
function run(cmd, args) { const r = spawnSync(cmd, args, {encoding: 'utf8', windowsHide: true, maxBuffer: 64e6}); if (r.status !== 0) throw Error(r.stderr || String(r.error)); return r.stdout + r.stderr; }
const ff = args => run('ffmpeg', ['-hide_banner', '-v', 'error', '-y', ...args]);
const probe = p => JSON.parse(run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', p]).trim());

const mp = abs('projects/small-window-game-design/project.json');
const m = read(mp), plan = read(path.join(__dirname, 'full-v2/plan.json'));
const offset = m.editing.intro?.seconds ?? 2, D = plan.seconds + offset, frames = plan.totalFrames + Math.round(offset * 60);
const music = {
  title: 'Nimbus', artist: 'Eveningland', library: 'YouTube Audio Library',
  file: 'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.mp3',
  licenseRecord: 'shared/assets/music/youtube-audio-library/Nimbus-Eveningland.LICENSE.md',
};
const gameGain = +(m.audio.gameAudioGain * 0.8).toFixed(4);
const assets = 'motion-canvas/src/projects/small-window-game-design/assets/';
const outputs = {
  audioMix: assets + 'final-mix-v4.m4a', editorAudioMix: assets + 'final-mix-v4.wav',
  videoClean: 'shared/output/motion-canvas/small-window-game-design-v4.mp4',
  videoBurnedCaptions: 'shared/output/motion-canvas/small-window-game-design-v4-subtitled.mp4',
};
// Picture sources: the v3 renders (intro + body), whose video streams are reused byte-for-byte.
const pictures = {videoClean: m.paths.videoClean, videoBurnedCaptions: m.paths.videoBurnedCaptions};
const windows = plan.scenes.map(s => [s.start + offset, s.start + offset + s.gameSeconds]);
const stage = process.argv[2];
fs.mkdirSync(work, {recursive: true});

if (stage === 'build') {
  if (+probe(abs(music.file)).format.duration < D) throw Error('Music shorter than video: add a 1s crossfade loop');
  const args = ['-i', abs(m.paths.narration)];
  plan.scenes.forEach(s => args.push('-i', path.join(__dirname, `full-v2/game-${s.id}.wav`)));
  args.push('-i', abs(music.file));
  const bgmIdx = plan.scenes.length + 1;
  // Each scene's source audio is delayed to its own gameplay window; nothing is concatenated.
  const placed = plan.scenes.map((s, i) =>
    `[${i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration=${s.gameSeconds},asetpts=N/SR/TB,` +
    `adelay=${Math.round(windows[i][0] * 1000)}:all=1,apad,atrim=duration=${D}[g${i}]`).join(';');
  const overlap = windows.map(([a, b]) => `if(between(t,${a},${b}),min(1,min((t-${a})/0.45,(${b}-t)/0.45)),0)`).join('+');
  const filter =
    `[0:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,adelay=${offset * 1000}:all=1,asetpts=N/SR/TB,apad,atrim=duration=${D},asplit=3[n][d1][d2];` +
    `${placed};${plan.scenes.map((_, i) => `[g${i}]`).join('')}amix=inputs=${plan.scenes.length}:normalize=0:duration=longest,atrim=duration=${D}[g];` +
    `[${bgmIdx}:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=${m.audio.bgmTargetLufs}:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,` +
    `volume='1-0.292054*(${overlap})':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${D - 0.45}:d=0.45[b];` +
    `[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280,volume=${gameGain},asplit=2[gd][gonly];` +
    `[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd];` +
    `[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgo];` +
    `[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true,asetpts=N/SR/TB,apad,atrim=end_sample=${Math.round(D * 48000)}[mix]`;
  write(path.join(work, 'mix-filter.txt'), filter);
  ff([...args, '-filter_complex', filter,
    '-map', '[mix]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', abs(outputs.editorAudioMix),
    '-map', '[bgo]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', path.join(work, 'background-only.wav'),
    '-map', '[gonly]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', path.join(work, 'game-only.wav')]);
  ff(['-i', abs(outputs.editorAudioMix), '-c:a', 'aac', '-b:a', '192k', abs(outputs.audioMix)]);
  for (const key of ['videoClean', 'videoBurnedCaptions']) {
    ff(['-i', abs(pictures[key]), '-i', abs(outputs.audioMix), '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy',
      '-t', String(D), '-movflags', '+faststart', abs(outputs[key])]);
  }
  console.log('Build complete');
} else if (stage === 'verify') {
  const level = (file, from, seconds) => {
    const out = run('ffmpeg', ['-hide_banner', '-nostats', '-ss', String(from), '-t', String(seconds), '-i', file, '-af', 'volumedetect', '-f', 'null', '-']);
    const mean = out.match(/mean_volume: (-?[\d.]+|-inf) dB/), max = out.match(/max_volume: (-?[\d.]+|-inf) dB/);
    return {mean: mean ? Number(mean[1]) : null, max: max ? Number(max[1]) : null};
  };
  const gameOnly = path.join(work, 'game-only.wav');
  const qa = {seconds: D, frames, gameGain, music, scenes: []};
  for (const [i, s] of plan.scenes.entries()) {
    const [a, b] = windows[i], end = offset + s.start + s.seconds;
    const inGame = level(gameOnly, a + 0.5, Math.max(0.5, b - a - 1));
    const inDiagram = level(gameOnly, b + 0.35, Math.max(0.2, end - b - 0.5));
    qa.scenes.push({id: s.id, gameWindow: [a, b], gameMeanDb: inGame.mean, diagramMaxDb: inDiagram.max});
    if (inDiagram.max !== null && inDiagram.max > -80) throw Error(`scene ${s.id}: game audio under the diagram (${inDiagram.max} dB)`);
  }
  const loud = run('ffmpeg', ['-hide_banner', '-nostats', '-i', abs(outputs.audioMix), '-af', 'ebur128=peak=true', '-f', 'null', '-']);
  qa.integratedLufs = Number(loud.match(/I:\s+(-?[\d.]+) LUFS/g).pop().match(/-?[\d.]+/)[0]);
  qa.truePeakDbtp = Number(loud.match(/Peak:\s+(-?[\d.]+) dBFS/g).pop().match(/-?[\d.]+/)[0]);
  qa.bgmOnlyEndMeanDb = level(abs(outputs.editorAudioMix), D - 3, 2).mean;
  const audioHashes = p => run('ffmpeg', ['-v', 'error', '-i', p, '-map', '0:a:0', '-c', 'copy', '-f', 'framehash', '-']).split('\n').filter(l => l && !l.startsWith('#')).map(l => l.split(',').at(-1).trim());
  const videoHashes = p => run('ffmpeg', ['-v', 'error', '-i', p, '-map', '0:v:0', '-c', 'copy', '-f', 'framehash', '-']).split('\n').filter(l => l && !l.startsWith('#')).map(l => l.split(',').at(-1).trim());
  const master = JSON.stringify(audioHashes(abs(outputs.audioMix)));
  qa.files = {};
  for (const key of ['videoClean', 'videoBurnedCaptions']) {
    const p = probe(abs(outputs[key])), v = p.streams.find(x => x.codec_type === 'video');
    if (+v.nb_frames !== frames || Math.abs(+p.format.duration - D) > 0.05) throw Error('Bad output ' + key);
    if (master !== JSON.stringify(audioHashes(abs(outputs[key])))) throw Error('Audio packets differ ' + key);
    if (JSON.stringify(videoHashes(abs(pictures[key]))) !== JSON.stringify(videoHashes(abs(outputs[key])))) throw Error('Picture changed ' + key);
    ff(['-i', abs(outputs[key]), '-f', 'null', '-']);
    qa.files[key] = {frames: +v.nb_frames, seconds: +p.format.duration, pictureUnchangedFrom: pictures[key]};
  }
  if (qa.truePeakDbtp > -1.5) throw Error(`True peak ${qa.truePeakDbtp} dBTP above -1.5`);
  write(path.join(work, 'qa.json'), qa);
  console.log(JSON.stringify(qa, null, 2));
} else if (stage === 'activate') {
  const qa = read(path.join(work, 'qa.json')), current = read(mp);
  const previousMusic = current.audio.backgroundMusic;
  current.audio.backgroundMusic = {
    required: true, approvalStatus: 'approved', approvedAt: '2026-09-29',
    approvalEvidence: '2026-09-29 user selected "Nimbus — Eveningland (추천)" after Discovery Content ID risk',
    title: music.title, artist: music.artist, library: music.library, license: 'YouTube Audio Library',
    attribution: 'Music: Nimbus — Eveningland (YouTube Audio Library)', file: music.file, licenseRecord: music.licenseRecord,
  };
  current.audio.replacedMusic = (current.audio.replacedMusic || []).concat([{title: previousMusic.title, artist: previousMusic.artist, reason: '2026-09-29 Content ID claim risk (claimed on play-first)'}]);
  current.audio.gameAudioGain = gameGain;
  current.audio.gameAudioGainDb = 20 * Math.log10(gameGain);
  current.audio.gameAudioGainReason = '2026-09-29 user: 게임구간만 조금 작게 유지, 지금 크기의 80% (0.5 x 0.8). Game audio only inside gameplay windows.';
  current.audio.gameAudioPlacement = 'per-scene adelay into its gameplay window; silent under diagrams (v3 concat drift fixed)';
  current.audio.mixStatus = 'v4-mixed-verified-awaiting-human-listening';
  current.audio.measuredIntegratedLufs = qa.integratedLufs;
  current.audio.measuredTruePeakDbtp = qa.truePeakDbtp;
  Object.assign(current.paths, outputs);
  current.finalRender = {...current.finalRender, kind: 'v4-audio-fix', qa: rel(path.join(work, 'qa.json')), frames: qa.frames, seconds: qa.seconds,
    pictureFrom: pictures};
  write(mp, current);
  console.log('Manifest activated (v4 audio)');
} else throw Error('Use build | verify | activate');
