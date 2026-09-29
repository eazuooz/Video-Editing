// v5 (2026-09-29): append the 10s membership thank-you page using the user's original member-list screenshot
// (profile images, names and badges exactly as supplied — no redraw), title "멤버쉽 후원 감사드립니다." (user wording).
// Audio is re-mixed from stems at body+10s: narration/game placement identical to v4, Nimbus continues through
// the outro and fades out only at the very end. Body picture is copied from the v4 renders.
// Usage: node projects/small-window-game-design/production/remix-v5-outro.cjs build | verify | activate
const fs = require('node:fs'), path = require('node:path'), {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..'), work = path.join(__dirname, 'mix-v5-outro');
const abs = p => path.join(root, p), rel = p => path.relative(root, p).replaceAll('\\', '/');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const write = (p, v) => { fs.mkdirSync(path.dirname(p), {recursive: true}); fs.writeFileSync(p, typeof v === 'string' ? v : JSON.stringify(v, null, 2) + '\n'); };
function run(cmd, args) { const r = spawnSync(cmd, args, {encoding: 'utf8', windowsHide: true, maxBuffer: 64e6}); if (r.status !== 0) throw Error(r.stderr || String(r.error)); return r.stdout + r.stderr; }
const ff = args => run('ffmpeg', ['-hide_banner', '-v', 'error', '-y', ...args]);
const probe = p => JSON.parse(run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', p]).trim());

const mp = abs('projects/small-window-game-design/project.json');
const m = read(mp), plan = read(path.join(__dirname, 'full-v2/plan.json'));
const introSeconds = m.editing.intro?.seconds ?? 2, outroSeconds = 10;
const body = plan.seconds + introSeconds, D = body + outroSeconds;
const bodyFrames = plan.totalFrames + Math.round(introSeconds * 60), frames = bodyFrames + outroSeconds * 60;
const outro = {
  screenshot: 'shared/assets/membership/member-list-20260929.png',
  title: 'shared/assets/membership/outro-title.txt',
  subtitle: 'shared/assets/membership/outro-subtitle.txt',
};
const music = m.audio.backgroundMusic;
const gameGain = m.audio.gameAudioGain;
const assets = 'motion-canvas/src/projects/small-window-game-design/assets/';
const outputs = {
  audioMix: assets + 'final-mix-v5.m4a', editorAudioMix: assets + 'final-mix-v5.wav',
  videoClean: 'shared/output/motion-canvas/small-window-game-design-v5.mp4',
  videoBurnedCaptions: 'shared/output/motion-canvas/small-window-game-design-v5-subtitled.mp4',
};
// Body pictures: the verified v4 renders (their video streams are reused byte-for-byte).
const pictures = {videoClean: 'shared/output/motion-canvas/small-window-game-design-v4.mp4', videoBurnedCaptions: 'shared/output/motion-canvas/small-window-game-design-v4-subtitled.mp4'};
const windows = plan.scenes.map(s => [s.start + introSeconds, s.start + introSeconds + s.gameSeconds]);
const font = 'C\\:/Windows/Fonts/malgunbd.ttf', fontRegular = 'C\\:/Windows/Fonts/malgun.ttf';
const esc = p => abs(p).replaceAll('\\', '/').replace(':', '\\:');
const stage = process.argv[2];
fs.mkdirSync(work, {recursive: true});

if (stage === 'build') {
  if (music.approvalStatus !== 'approved') throw Error('Music approval missing');
  if (+probe(abs(music.file)).format.duration < D) throw Error('Music shorter than video: add a 1s crossfade loop');
  // 1) Outro picture: white research-paper page, title/subtitle left, original screenshot at full height on the right.
  const outroClip = path.join(work, 'outro-10s.mp4');
  const shotHeight = 900, shotWidth = Math.round(498 * shotHeight / 1033), shotX = 1920 - 96 - shotWidth, shotY = 90;
  const page =
    `[1:v]scale=-1:${shotHeight}:flags=lanczos,format=rgba[shot];` +
    `[0:v][shot]overlay=x=${shotX}:y=${shotY}:shortest=1,` +
    `drawbox=x=${shotX - 2}:y=${shotY - 2}:w=${shotWidth + 4}:h=${shotHeight + 4}:color=0xcbd0d6:t=2,` +
    `drawtext=fontfile='${fontRegular}':text='MEMBERSHIP':x=96:y=372:fontsize=26:fontcolor=0x2f5faa,` +
    `drawtext=fontfile='${font}':textfile='${esc(outro.title)}':x=96:y=420:fontsize=64:fontcolor=0x202020,` +
    `drawtext=fontfile='${fontRegular}':textfile='${esc(outro.subtitle)}':x=96:y=520:fontsize=32:fontcolor=0x737373,` +
    `fade=t=in:st=0:d=0.4:color=white,fade=t=out:st=${outroSeconds - 0.5}:d=0.5:color=white,format=yuv420p`;
  ff(['-f', 'lavfi', '-i', `color=c=white:s=1920x1080:r=60:d=${outroSeconds}`, '-loop', '1', '-framerate', '60', '-i', abs(outro.screenshot),
    '-filter_complex', page, '-t', String(outroSeconds), '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p',
    '-r', '60', '-frames:v', String(outroSeconds * 60), '-video_track_timescale', '90000', outroClip]);
  ff(['-ss', '5', '-i', outroClip, '-frames:v', '1', '-update', '1', path.join(work, 'outro-still.png')]);

  // 2) Audio from stems at body + outro length (same placement as v4; BGM carries through the outro).
  const args = ['-i', abs(m.paths.narration)];
  plan.scenes.forEach(s => args.push('-i', path.join(__dirname, `full-v2/game-${s.id}.wav`)));
  args.push('-i', abs(music.file));
  const bgmIdx = plan.scenes.length + 1;
  const placed = plan.scenes.map((s, i) =>
    `[${i + 1}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration=${s.gameSeconds},asetpts=N/SR/TB,` +
    `adelay=${Math.round(windows[i][0] * 1000)}:all=1,apad,atrim=duration=${D}[g${i}]`).join(';');
  const overlap = windows.map(([a, b]) => `if(between(t,${a},${b}),min(1,min((t-${a})/0.45,(${b}-t)/0.45)),0)`).join('+');
  const filter =
    `[0:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,adelay=${introSeconds * 1000}:all=1,asetpts=N/SR/TB,apad,atrim=duration=${D},asplit=3[n][d1][d2];` +
    `${placed};${plan.scenes.map((_, i) => `[g${i}]`).join('')}amix=inputs=${plan.scenes.length}:normalize=0:duration=longest,atrim=duration=${D}[g];` +
    `[${bgmIdx}:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=${m.audio.bgmTargetLufs}:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,` +
    `volume='1-0.292054*(${overlap})':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${D - 0.45}:d=0.45[b];` +
    `[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280,volume=${gameGain}[gd];` +
    `[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd];` +
    `[gd][bd]amix=inputs=2:normalize=0[bg];` +
    `[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true,asetpts=N/SR/TB,apad,atrim=end_sample=${Math.round(D * 48000)}[mix]`;
  write(path.join(work, 'mix-filter.txt'), filter);
  ff([...args, '-filter_complex', filter, '-map', '[mix]', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', abs(outputs.editorAudioMix)]);
  ff(['-i', abs(outputs.editorAudioMix), '-c:a', 'aac', '-b:a', '192k', abs(outputs.audioMix)]);

  // 3) Picture: v4 body video stream + outro clip (stream copy), then the new mix.
  // The clean and captioned bodies use different track timescales (90000 vs 15360); the outro must match each
  // body's timescale or the concat demuxer silently drops it.
  for (const key of ['videoClean', 'videoBurnedCaptions']) {
    const bodyOnly = path.join(work, `${key}-body.mp4`);
    ff(['-i', abs(pictures[key]), '-map', '0:v:0', '-c', 'copy', bodyOnly]);
    const timescale = probe(bodyOnly).streams.find(x => x.codec_type === 'video').time_base.split('/')[1];
    const matchedOutro = path.join(work, `${key}-outro.mp4`);
    ff(['-i', outroClip, '-c', 'copy', '-video_track_timescale', timescale, matchedOutro]);
    const list = path.join(work, `${key}-concat.txt`);
    write(list, [bodyOnly, matchedOutro].map(p => `file '${p.replaceAll('\\', '/')}'`).join('\n'));
    ff(['-f', 'concat', '-safe', '0', '-i', list, '-i', abs(outputs.audioMix), '-map', '0:v', '-map', '1:a', '-c', 'copy',
      '-t', String(D), '-movflags', '+faststart', abs(outputs[key])]);
  }
  console.log('Build complete');
} else if (stage === 'verify') {
  const level = (file, from, seconds) => {
    const out = run('ffmpeg', ['-hide_banner', '-nostats', '-ss', String(from), '-t', String(seconds), '-i', file, '-af', 'volumedetect', '-f', 'null', '-']);
    const mean = out.match(/mean_volume: (-?[\d.]+) dB/);
    return mean ? Number(mean[1]) : null;
  };
  const qa = {seconds: D, frames, bodySeconds: body, outroSeconds, outro, files: {}};
  const loud = run('ffmpeg', ['-hide_banner', '-nostats', '-i', abs(outputs.audioMix), '-af', 'ebur128=peak=true', '-f', 'null', '-']);
  qa.integratedLufs = Number(loud.match(/I:\s+(-?[\d.]+) LUFS/g).pop().match(/-?[\d.]+/)[0]);
  qa.truePeakDbtp = Number(loud.match(/Peak:\s+(-?[\d.]+) dBFS/g).pop().match(/-?[\d.]+/)[0]);
  qa.outroBgmMeanDb = level(abs(outputs.editorAudioMix), body + 1, 7);
  if (qa.outroBgmMeanDb === null || qa.outroBgmMeanDb < -45) throw Error('BGM missing under the outro');
  if (qa.truePeakDbtp > -1.5) throw Error('True peak above -1.5 dBTP');
  // Compare decoded frames: concat re-inserts SPS/PPS into keyframe packets, so packet hashes can differ
  // while every decoded body frame is identical.
  const videoHashes = p => run('ffmpeg', ['-v', 'error', '-i', p, '-map', '0:v:0', '-frames:v', String(bodyFrames), '-f', 'framemd5', '-']).split('\n').filter(l => l && !l.startsWith('#')).map(l => l.split(',').at(-1).trim());
  for (const key of ['videoClean', 'videoBurnedCaptions']) {
    const p = probe(abs(outputs[key])), v = p.streams.find(x => x.codec_type === 'video');
    if (+v.nb_frames !== frames || Math.abs(+p.format.duration - D) > 0.05) throw Error(`Bad output ${key}: ${v.nb_frames} frames`);
    const before = videoHashes(abs(pictures[key])), after = videoHashes(abs(outputs[key]));
    if (JSON.stringify(before) !== JSON.stringify(after.slice(0, before.length))) throw Error('Body picture changed ' + key);
    ff(['-i', abs(outputs[key]), '-f', 'null', '-']);
    ff(['-ss', String(body + 5), '-i', abs(outputs[key]), '-frames:v', '1', '-update', '1', path.join(work, `${key}-outro.jpg`)]);
    qa.files[key] = {frames: +v.nb_frames, seconds: +p.format.duration, bodyPictureFrom: pictures[key]};
  }
  write(path.join(work, 'qa.json'), qa);
  console.log(JSON.stringify(qa, null, 2));
} else if (stage === 'activate') {
  const qa = read(path.join(work, 'qa.json')), current = read(mp);
  Object.assign(current.paths, outputs);
  current.video.durationSeconds = D;
  current.membershipOutro = {...(current.membershipOutro || {}), enabled: true, durationSeconds: outroSeconds, appliedToFinal: true,
    kind: 'original-screenshot', title: '멤버쉽 후원 감사드립니다.', titleEvidence: '2026-09-29 user: 멤버쉽 후원 감사드립니다. 페이지 추가해줘 / 이 이미지를 그대로 맨뒤에',
    screenshot: outro.screenshot, verifiedIn: [outputs.videoClean + ` @${(body + 5).toFixed(1)}s`]};
  current.editing.outro = {...(current.editing.outro || {}), seconds: outroSeconds, title: '멤버쉽 후원 감사드립니다.', source: outro.screenshot};
  current.audio.mixStatus = 'v5-with-outro-verified-awaiting-human-listening';
  current.audio.measuredIntegratedLufs = qa.integratedLufs;
  current.audio.measuredTruePeakDbtp = qa.truePeakDbtp;
  current.finalRender = {...current.finalRender, kind: 'v5-intro-body-outro', qa: rel(path.join(work, 'qa.json')), frames: qa.frames, seconds: qa.seconds};
  write(mp, current);
  console.log('Manifest activated (v5 with outro)');
} else throw Error('Use build | verify | activate');
