// Build the five 19.5s Super Mario Odyssey example clips (Archive 64) for play-first.
// Final in/out points were chosen from 1-2s contact sheets of the HQ windows (fetch-play-first-odyssey.cjs).
// Source sound is preserved; the mixer sets its level. Usage: node scripts/prepare-play-first-examples.cjs
const fs = require('node:fs'), path = require('node:path'), {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const cache = path.join(root, 'shared/output/play-first/media-cache');
const outDir = path.join(root, 'motion-canvas/src/projects/play-first/assets/broll');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects/play-first/project.json'), 'utf8'));
const exampleSeconds = manifest.editing.exampleSeconds;
const src = {
  p1: 'https://www.youtube.com/watch?v=4s8UTTRLiu4',
  p2: 'https://www.youtube.com/watch?v=cSig9xMlEEE',
};
// [window file stem, window start in source, in, out] — in/out are relative to the window file.
const scenes = [
  {scene: '01', label: '짧은 오프닝 뒤 착지·첫 조작 안내, 달리고 뛰기', cuts: [['p1-80-125', 80, 25.5, 45.0], ['p1-125-135', 125, 0.5, 8.0]]},
  {scene: '02', label: '모자로 코인·상자, 멍멍이 캡처와 튕겨 보내기', cuts: [['p1-250-282', 250, 11.5, 21.5], ['p2-110-135', 110, 0.0, 9.5], ['p2-110-135', 110, 13.0, 20.5]]},
  {scene: '03', label: '싸움 한복판의 비행선 오프닝과 결혼식 대사', cuts: [['p1-0-30', 0, 7.5, 17.5], ['p1-50-72', 50, 10.5, 20.0], ['p1-0-30', 0, 22.0, 29.5]]},
  {scene: '04', label: '폭포의 나라 공룡에게 다가가 캡처하고 돌진', cuts: [['p2-715-762', 715, 14.0, 41.0]]},
  {scene: '05', label: '본편 길 위의 개구리 캡처, 첫 보스 뒤 타이틀', cuts: [['p1-470-502', 470, 22.0, 31.0], ['p1-685-730', 685, 14.5, 32.5]]},
];
const run = (cmd, args) => {
  const r = spawnSync(cmd, args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024});
  if (r.status !== 0) throw Error(`${cmd} failed: ${(r.stderr || '').slice(-2000)}`);
  return r.stdout;
};
fs.mkdirSync(outDir, {recursive: true});
const reports = [];
for (const {scene, label, cuts} of scenes) {
  const total = cuts.reduce((sum, [, , a, b]) => sum + (b - a), 0);
  if (Math.abs(total - exampleSeconds) > 0.01) throw Error(`scene ${scene}: ${total}s != ${exampleSeconds}s`);
  const args = ['-hide_banner', '-v', 'error', '-y'];
  cuts.forEach(([stem, , a, b]) => args.push('-ss', String(a), '-t', String(b - a), '-i', path.join(cache, `archive64-odyssey-${stem}.mp4`)));
  const parts = cuts.map((_, i) =>
    `[${i}:v]scale=1920:1080:flags=lanczos,fps=60,setsar=1,format=yuv420p,setpts=PTS-STARTPTS[v${i}];` +
    `[${i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a${i}]`).join(';');
  const concat = cuts.map((_, i) => `[v${i}][a${i}]`).join('') + `concat=n=${cuts.length}:v=1:a=1[v][a]`;
  const output = path.join(outDir, `scene${scene}.mp4`);
  args.push('-filter_complex', `${parts};${concat}`, '-map', '[v]', '-map', '[a]',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-g', '60', '-c:a', 'aac', '-b:a', '192k',
    '-t', String(exampleSeconds), '-movflags', '+faststart', output);
  run('ffmpeg', args);
  const probe = JSON.parse(run('ffprobe', ['-v', 'error', '-count_frames', '-show_entries',
    'stream=codec_type,nb_read_frames,width,height:format=duration', '-of', 'json', output]));
  const video = probe.streams.find(s => s.codec_type === 'video');
  const frames = Number(video.nb_read_frames);
  if (frames !== Math.round(exampleSeconds * 60) || !probe.streams.some(s => s.codec_type === 'audio')) {
    throw Error(`scene ${scene}: unexpected output ${JSON.stringify(probe)}`);
  }
  run('ffmpeg', ['-v', 'error', '-i', output, '-f', 'null', '-']);
  reports.push({
    scene, label, file: path.relative(root, output).replaceAll('\\', '/'), seconds: exampleSeconds, frames,
    cuts: cuts.map(([stem, windowStart, a, b]) => ({source: src[stem.slice(0, 2)], start: +(windowStart + a).toFixed(2), end: +(windowStart + b).toFixed(2)})),
    audioPreserved: true, fullDecodePassed: true,
  });
  console.log(`scene${scene}.mp4 ${frames} frames`);
}
fs.writeFileSync(path.join(outDir, 'media-report.json'), JSON.stringify({
  createdAt: new Date().toISOString(), permission: 'https://www.nintblkc.com/archive-64',
  note: 'Cut starts are window-relative; source times approximate (yt-dlp section download).', reports,
}, null, 2) + '\n');
