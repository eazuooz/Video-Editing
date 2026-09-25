// Download only the Archive 64 Super Mario Odyssey windows planned in projects/play-first/sources/odyssey-cuts.json.
// Permission: each source description + https://www.nintblkc.com/archive-64. Proxies are preserved.
// Usage: node scripts/fetch-play-first-odyssey.cjs
const fs = require('node:fs'), path = require('node:path'), {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const cacheDir = 'shared/output/play-first/media-cache';
const ids = {p1: '4s8UTTRLiu4', p2: 'cSig9xMlEEE'};
// [part, start, end] — a few seconds of margin around each candidate cut for final in/out selection.
const windows = [
  ['p1', 0, 30], ['p1', 50, 72], ['p1', 80, 125], ['p1', 125, 135], ['p1', 250, 282],
  ['p1', 470, 502], ['p1', 685, 730], ['p2', 90, 112], ['p2', 110, 135], ['p2', 715, 762],
];
for (const [part, start, end] of windows) {
  const output = `${cacheDir}/archive64-odyssey-${part}-${start}-${end}.mp4`;
  if (fs.existsSync(path.join(root, output))) { console.log('Cached ' + output); continue; }
  const r = spawnSync(path.join(root, 'qwen3-tts/.venv/Scripts/python.exe'),
    ['-X', 'utf8', '-m', 'yt_dlp', '--no-progress', '--no-warnings', '--js-runtimes', 'node', '-f', '299+140',
      '--download-sections', `*${start}-${end}`, '--force-keyframes-at-cuts', '--merge-output-format', 'mp4',
      '-o', output, `https://www.youtube.com/watch?v=${ids[part]}`],
    {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 32 * 1024 * 1024});
  if (r.status !== 0) throw Error((r.stderr || r.stdout).slice(-3000));
  console.log(`Downloaded ${part} ${start}-${end}`);
}
